import re
import json
from typing import Dict, Any

# A hard programmatic post-check that intercepts any clinical diagnostic wording
FORBIDDEN_TERMS = [
    r"\bdiagnos(e|is|ed|ing)\b",
    r"\btreat(ment|ed|ing)?\b",
    r"\bprescri(be|ption)\b",
    r"\bsyndrome\b",
    r"\bdisease\b",
    r"\bpatholog(y|ical)\b"
]

def sanitize_agent_output(text: str) -> str:
    """
    Blocks and redacts forbidden diagnostic claims to enforce the Science Boundary.
    """
    for pattern in FORBIDDEN_TERMS:
        if re.search(pattern, text, re.IGNORECASE):
            # We must fail safely or replace it with a non-diagnostic fallback
            return "Alert: Telemetry deviation detected. Consult flight surgeon logs. Citing relevant NASA literature."
    return text

def build_evidence_card(alert: Dict[str, Any], cached_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generates an evidence-backed factual summary linking directly to open NASA literature.
    This acts as the deterministic 'Agent' output without requiring a live LLM call 
    (satisfying the offline requirement).
    """
    if cached_metadata is None:
        # Fallback to local cache structure
        study_id = "OSD-87"
        study_url = "https://osdr.nasa.gov/osdr/data/osd/files/87.1"
        study_title = "Spaceflight effects on cardiovascular autonomic regulation"
    else:
        study_id = cached_metadata.get("study_id", "OSD-87")
        study_url = cached_metadata.get("url", "https://osdr.nasa.gov/osdr/data/osd/files/87.1")
        study_title = cached_metadata.get("title", "Spaceflight effects on cardiovascular autonomic regulation")
        
    rule = alert.get("rule", "Unknown anomaly")
    z_score = alert.get("z", 0.0)
    current = alert.get("current", 0.0)
    baseline_mean = alert.get("baseline_mean", 0.0)
    
    summary = (
        f"Deviation recorded: {rule} with Z-score {z_score}. "
        f"Observed value ({current}) deviated from personal mean ({baseline_mean}). "
        f"Literature context: {study_title}. "
        f"Cataloged under NASA OSDR study {study_id}."
    )
    
    # Strictly sanitize the output to avoid accidental diagnostic language
    clean_text = sanitize_agent_output(summary)
    
    return {
        "text": clean_text,
        "study_id": study_id,
        "source_url": study_url,
        "raw_alert": alert
    }
