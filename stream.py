import os
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from src.api.vision import router as vision_router

app = FastAPI()

app.include_router(vision_router, prefix="/api/vision")

# Allow CORS for the frontend to connect from a different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enforce offline mode by default until wristband is connected
OFFLINE_MODE = os.getenv("OFFLINE", "1") == "1"
FIXTURE_PATH = Path("demo_fixtures/vitals.json")

# In-memory rolling buffer for real-time calculations
telemetry_buffer = []

class VitalsRecord(BaseModel):
    heart_rate: float
    hrv: float
    spo2: float
    exercise_posture_score: float = 1.0
    detected_expression: str = "neutral"

@app.post("/api/telemetry/ingest")
async def ingest_vitals(record: VitalsRecord):
    """
    Endpoint for the physical ESP32 and HuskyLens to post live data.
    """
    data = record.dict()
    telemetry_buffer.append(data)
    # Keep only the last 300 records in memory
    if len(telemetry_buffer) > 300:
        telemetry_buffer.pop(0)
    return {"status": "ok", "buffer_size": len(telemetry_buffer)}

# Global state for the autonomous guardian script to update
latest_autonomous_action = "Initializing autonomous AI monitoring..."

class ActionRecord(BaseModel):
    action_text: str

@app.post("/api/telemetry/action")
async def update_action(record: ActionRecord):
    global latest_autonomous_action
    latest_autonomous_action = record.action_text
    return {"status": "ok"}

@app.websocket("/ws/telemetry")
async def stream_telemetry(websocket: WebSocket):
    """
    WebSocket endpoint for the Frontend Web Console to receive live telemetry.
    """
    await websocket.accept()
    
    # Offline safety net: fall back to pre-recorded fixture if offline or hardware idle
    if OFFLINE_MODE or not telemetry_buffer:
        print("Starting offline playback stream...")
        if not FIXTURE_PATH.exists():
            await websocket.send_json({"error": f"Fixture file not found at {FIXTURE_PATH}"})
            await websocket.close()
            return
            
        with open(FIXTURE_PATH, "r") as f:
            demo_data = json.load(f)
            
        playback_speed = 1.0 # Can be made adjustable
        for index, row in enumerate(demo_data):
            payload = {
                "index": index,
                "source": "Simulated Telemetry",
                "telemetry": row,
                "autonomous_action": latest_autonomous_action
            }
            try:
                await websocket.send_json(payload)
                await asyncio.sleep(1.0 / playback_speed)
            except Exception as e:
                print(f"WebSocket disconnected: {e}")
                break
    else:
        print("Starting live hardware stream...")
        while True:
            if telemetry_buffer:
                latest = telemetry_buffer[-1]
                try:
                    await websocket.send_json({
                        "source": "Hardware Feed", 
                        "telemetry": latest,
                        "autonomous_action": latest_autonomous_action
                    })
                    await asyncio.sleep(1.0)
                except Exception as e:
                    print(f"WebSocket disconnected: {e}")
                    break
