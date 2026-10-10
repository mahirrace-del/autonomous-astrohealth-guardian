from mcp.server.mcpserver import MCPServer
import sys
import logging
import json
import os
import asyncio
from dotenv import load_dotenv

# We need the google-genai library and our existing vision logic
from google import genai
from src.api.vision import fetch_huskylens_image

load_dotenv()

logger = logging.getLogger('Xiaozhi_Nasa_MCP')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Create an MCP server
mcp = MCPServer("AstronautHealthMonitor")

@mcp.tool()
def get_astronaut_vitals() -> dict:
    """Use this tool to get the current health vitals of the astronaut. It returns heart rate, blood pressure, oxygen levels, etc."""
    try:
        data_path = os.path.join(os.path.dirname(__file__), "data", "vitals.json")
        if not os.path.exists(data_path):
            return {"success": False, "message": "No telemetry data available yet."}
        with open(data_path, "r", encoding="utf-8") as f:
            vitals = json.load(f)
        return {"success": True, "vitals": vitals}
    except Exception as e:
        logger.error(f"Error reading vitals: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
async def ask_huskylens_vision(question: str, mode: str = "Facial Expression Recognition") -> dict:
    """Use this tool to physically look at the astronaut through the HuskyLens camera and ask a visual question. 
    Modes available: 'Facial Expression Recognition', 'Fall Detection', 'Object Recognition'."""
    try:
        # Fetch the live image from the HuskyLens
        img = await fetch_huskylens_image(mode)
        if not img:
            return {"success": False, "message": "Failed to connect to HuskyLens camera over Wi-Fi."}
        
        # Query Gemini 3.8 Flash
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[
                "You are an AI assistant in an astronaut health monitoring system. "
                "You are viewing a live feed from the astronaut's HuskyLens camera. "
                "Answer the user's question very concisely (under 100 words) based on what you see in the image.",
                img,
                question
            ]
        )
        return {"success": True, "answer": response.text}
    except Exception as e:
        logger.error(f"Error in vision tool: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
