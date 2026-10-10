import asyncio
import time
import logging
from google import genai
from dotenv import load_dotenv

from src.api.vision import fetch_huskylens_image

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("AutonomousGuardian")

# Load environment variables (API Key)
load_dotenv()

async def autonomous_monitoring_loop():
    """
    Autonomously cycles the HuskyLens through different modes to get a comprehensive
    context of the astronaut's environment and state, using Gemini for analysis.
    """
    logger.info("Initializing Autonomous Guardian Routine...")
    
    # Modes to cycle through for full situational awareness
    modes = [
        "Facial Expression Recognition",
        "Fall Detection",
        "Object Recognition"
    ]
    
    client = genai.Client()

    while True:
        for mode in modes:
            logger.info(f"Switching HuskyLens to mode: {mode}")
            
            try:
                # 1. Autonomously switch the camera mode and fetch the frame
                img = await fetch_huskylens_image(mode)
                
                if not img:
                    logger.warning(f"Failed to retrieve image for {mode}. Skipping...")
                    continue
                
                logger.info(f"Image captured. Analyzing via Gemini 3.8 Flash...")
                
                # 2. Formulate context-specific prompt based on the mode
                if mode == "Facial Expression Recognition":
                    prompt = "Analyze this astronaut's face. What is their current emotional and physical state? (Keep it to 1 sentence)"
                elif mode == "Fall Detection":
                    prompt = "Check the astronaut's posture and position. Is there any indication of a fall, slump, or physical distress? (Keep it to 1 sentence)"
                elif mode == "Object Recognition":
                    prompt = "What objects are currently around the astronaut? Are there any hazardous tools or items in their workspace? (Keep it to 1 sentence)"
                
                # 3. Request AI analysis
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=[prompt, img]
                )
                
                # 4. Log the autonomous finding
                action_text = f"[{mode}] {response.text.strip()}"
                logger.info(f"🧠 ANALYSIS {action_text}")
                
                # 5. Push this finding to the web dashboard backend
                try:
                    import requests
                    requests.post(
                        "http://127.0.0.1:8000/api/telemetry/action",
                        json={"action_text": action_text},
                        timeout=2
                    )
                except Exception as post_err:
                    logger.error(f"Failed to push action to dashboard: {post_err}")
                
                # Wait 30 seconds before switching to the next context to prevent API rate limits!
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in autonomous loop during {mode}: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(autonomous_monitoring_loop())
    except KeyboardInterrupt:
        logger.info("Autonomous Guardian shutdown.")
