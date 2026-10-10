import io
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
from PIL import Image
import base64
from typing import Optional

from mcp import ClientSession
from mcp.client.sse import sse_client
from contextlib import AsyncExitStack

# Monkeypatch httpx-sse due to HuskyLens bug
import httpx2._sse
original_check = httpx2._sse.EventSource._check_content_type
def patched_check(self) -> None:
    content_type, _, _ = self._response.headers.get("content-type", "").partition(";")
    if "text/event-stream" in content_type:
        return
    original_check(self)
httpx2._sse.EventSource._check_content_type = patched_check


router = APIRouter()

class AskRequest(BaseModel):
    question: str
    algorithm: str = "Facial Expression Recognition"  # Default algorithm

async def fetch_huskylens_image(algorithm_name: str) -> Optional[Image.Image]:
    """Fetches a real-time recognition frame from HuskyLens via MCP."""
    algorithm_map = {
        "Face Recognition": 1,
        "Object Recognition": 2,
        "Object Tracking": 3,
        "Color Recognition": 4,
        "Object Classification": 5,
        "Self-Learning Classifier": 6,
        "Instance Segmentation": 7,
        "Hand Recognition": 8,
        "Pose Recognition": 9,
        "LPR": 10,
        "Optical Char Recognition": 11,
        "Line Tracking": 12,
        "Facial Expression Recognition": 13,
        "Gaze Direction Detection": 14,
        "Orientation Detection": 15,
        "Tag Recognition": 16,
        "Barcode Recognition": 17,
        "QR Code Recognition": 18,
        "Fall Detection": 19,
        "Depth Detection": 20
    }
    
    algo_id = algorithm_map.get(algorithm_name, 1)
    
    try:
        async with AsyncExitStack() as stack:
            streams = await stack.enter_async_context(sse_client("http://192.168.0.249:3000/sse"))
            session = await stack.enter_async_context(ClientSession(streams[0], streams[1]))
            await session.initialize()

            # Switch mode
            try:
                await session.call_tool("self.manage_applications.switch_application", {"algorithm": algorithm_name})
            except Exception as e:
                print(f"Warning: Failed to switch to {algorithm_name}: {e}")
                
            await asyncio.sleep(1) # wait for mode to switch and camera to stabilize

            # Get frame
            res = await session.call_tool("self.get_recognition_result", {"algorithm": algo_id})
            
            for content in res.content:
                if content.type == "image":
                    image_data = base64.b64decode(content.data)
                    return Image.open(io.BytesIO(image_data))
                    
            print("No image data found in HuskyLens response.")
            return None
    except Exception as e:
        print(f"Error communicating with HuskyLens: {e}")
        return None

@router.post("/ask")
async def ask_vision(req: AskRequest):
    img = await fetch_huskylens_image(req.algorithm)
    
    if not img:
        return JSONResponse({"status": "error", "message": "Failed to capture image from HuskyLens"}, status_code=500)
    
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[
                "You are an AI assistant in an astronaut health monitoring system. "
                "You are viewing a live feed from the astronaut's HuskyLens camera. "
                "Answer the user's question concisely based on what you see in the image.",
                img,
                req.question
            ]
        )
        return {"status": "success", "answer": response.text}
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return JSONResponse({"status": "error", "message": f"Gemini AI error: {e}"}, status_code=500)


from fastapi.responses import StreamingResponse

async def mjpeg_frame_generator():
    """Continuously fetches frames from HuskyLens and yields them as an MJPEG stream."""
    try:
        async with AsyncExitStack() as stack:
            streams = await stack.enter_async_context(sse_client("http://192.168.0.249:3000/sse"))
            session = await stack.enter_async_context(ClientSession(streams[0], streams[1]))
            await session.initialize()
            
            while True:
                try:
                    # Using Facial Expression Recognition (algo 13) as a default to get frames
                    res = await session.call_tool("self.get_recognition_result", {"algorithm": 13})
                    
                    frame_bytes = None
                    for content in res.content:
                        if content.type == "image":
                            frame_bytes = base64.b64decode(content.data)
                            break
                            
                    if frame_bytes:
                        # Yield the frame in multipart format
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                        
                    await asyncio.sleep(0.5) # Poll at ~2 FPS to avoid overwhelming the camera
                except Exception as e:
                    print(f"Error fetching stream frame: {e}")
                    await asyncio.sleep(2)
    except Exception as e:
        print(f"Error in stream generator: {e}")


@router.get("/feed")
async def vision_feed():
    """Returns a live MJPEG stream from the HuskyLens."""
    return StreamingResponse(mjpeg_frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

