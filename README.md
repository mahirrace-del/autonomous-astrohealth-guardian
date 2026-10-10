# Autonomous AstroHealth Guardian

**NASA Space Apps Challenge 2026**
**Challenge:** Create Health Monitoring Software for Astronauts on Space Missions

## High-Level Summary
On deep-space missions, astronauts are months away from medical facilities. Relying solely on raw biometric data (like heart rate) lacks the context needed to accurately assess health—for instance, a high heart rate during exercise is normal, but dangerous during sleep. Furthermore, using Generative AI to diagnose medical issues is highly risky and prone to hallucinations.

We built the **Autonomous AstroHealth Guardian**, a local, offline-first system that combines biometric wristband data with visual context. By integrating a HuskyLens 2 AI Camera into the spacecraft habitat, our deterministic Python backend tracks the astronaut's context (e.g., Facial Expression Recognition, Fall Detection, Object Recognition). When a deviation is detected, the system does not guess a diagnosis; instead, it automatically queries the **NASA Open Science Data Repository (OSDR)** to provide peer-reviewed literature related to the anomaly, ensuring safe, evidence-based context for the crew.

## How It Works
1. **Raw Vitals:** A simulated biometric wristband tracks Heart Rate and SpO2.
2. **Context Engine (HuskyLens):** A local edge-AI camera observes the astronaut, providing state context (Sleeping, Exercising, Emotional State, Fall Detection).
3. **Deterministic Backend:** Python scripts securely analyze the combined data offline.
4. **NASA Explainer Agent:** When an anomaly occurs, an agent fetches factual metadata from NASA OSDR (Study OSD-87) to contextualize the event.

## NASA Data Sources Used
* **NASA Open Science Data Repository (OSDR)**
* **Study Used:** OSD-87: *Spaceflight effects on cardiovascular autonomic regulation*
* **Link:** [https://osdr.nasa.gov/osdr/data/osd/files/87.1](https://osdr.nasa.gov/osdr/data/osd/files/87.1)
* **Purpose:** To provide factual, peer-reviewed spaceflight literature to the astronaut when an anomaly is detected, rather than allowing the AI to hallucinate medical advice.

## Repository Structure
- `/src`: Contains the deterministic Python computation files and the Explainer Agent logic.
- `/web`: The offline-first HTML/JS/CSS dashboard interface.
- `/docs`: Contains our `AI_USE.md` file declaring our usage of Generative AI during the hackathon.

## License
Apache License 2.0
