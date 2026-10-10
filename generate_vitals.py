import json
import random
from pathlib import Path

def generate_vitals():
    data = []
    # Base values for a healthy astronaut
    base_hr = 70.0
    base_hrv = 55.0
    base_spo2 = 98.5
    
    for i in range(600):
        # Introduce an intentional anomaly around second 60 for the Killer Demo
        if 60 <= i <= 105:
            # Anomaly: Heart rate spikes, HRV drops, SpO2 drops, posture degrades, emotion becomes fatigued
            hr = base_hr + random.uniform(25.0, 35.0)
            hrv = base_hrv - random.uniform(20.0, 25.0) # Significant drop in HRV
            spo2 = base_spo2 - random.uniform(4.0, 6.0)
            posture = random.uniform(0.3, 0.5) # Poor posture
            expression = "fatigued"
        else:
            # Normal microgravity variations
            hr = base_hr + random.uniform(-5.0, 5.0)
            hrv = base_hrv + random.uniform(-3.0, 3.0)
            spo2 = base_spo2 + random.uniform(-1.0, 1.0)
            posture = random.uniform(0.85, 1.0) # Good posture
            expression = "neutral"
            
        record = {
            "heart_rate": round(hr, 2),
            "hrv": round(hrv, 2),
            "spo2": round(spo2, 2),
            "sleep_hours": 7.5,
            "core_temperature": round(36.8 + random.uniform(-0.2, 0.2), 2),
            "exercise_minutes": 45,
            "exercise_posture_score": round(posture, 2),
            "detected_expression": expression
        }
        data.append(record)
        
    out_dir = Path(__file__).parent
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "vitals.json"
    
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully generated 600 records of simulated telemetry at {out_path}")

if __name__ == "__main__":
    generate_vitals()
