# Use of AI in this project

As per the NASA Space Apps 2026 rules, this document explains exactly how Artificial Intelligence was used in the creation of this project.

## AI Tools Used
* **Antigravity IDE (Agentic AI Assistant):** Used for code scaffolding, Python backend refactoring, creating WebSocket servers, and generating project documentation.
* **Gemini 3.8 Flash (Via API):** Used inside the project code (`autonomous_guardian.py`) strictly as an explainer agent to parse HuskyLens visual data and map it to NASA OSDR studies.
* **AI Video Generators (Midjourney, Runway Gen-3, Luma Dream Machine):** Used to generate the storyboard visualizations for our 240-second pitch video because we did not have physical access to a mocked-up spacecraft interior.

## What the AI Did
* Built the initial scaffold for the FastAPI WebSockets and the local Python HTTP server.
* Wrote the HTML/CSS for the offline-capable Web Dashboard interface.
* Designed the highly-detailed text-to-video prompts used to generate the cinematic pitch video.

## What the AI Did NOT Do
* **The AI did not perform any medical diagnosis.** All anomaly detection logic (like Fall Detection and Vitals Deviations) is written in deterministic, heavily tested Python code located in `src/compute/`. The AI is strictly barred from diagnosing conditions.
* The hardware integration and overall architectural design of combining HuskyLens context with wearable data was entirely our team's creative concept.

## Example Prompts Used
**For the Agentic Code Generation:**
> *"Write a FastAPI websocket server that takes the JSON data from the HuskyLens detection loop and broadcasts it to a local HTML dashboard."*

**For the Video Generation:**
> *"First-person POV shot from the perspective of a digital camera screen. We are looking through the lens of an AI sensor. In the center of the frame, a young astronaut wearing a dark blue NASA jumpsuit is working at a control panel. Overlaying the astronaut are high-tech digital HUD elements tracking their face. Cinematic lighting, 8k resolution, ARRI Alexa 65, clean NASA spacecraft interior."*
