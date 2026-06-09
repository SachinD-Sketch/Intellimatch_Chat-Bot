import json
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "data"
SKILL_FILE = DATA_DIR / "sample_skill_matrix.json"
AVAIL_FILE = DATA_DIR / "availability.json"

CAP_MAP = {
    "Core": "Workfront Core",
    "Planning": "Workfront Planning",
    "Fusion": "Workfront Fusion",
    "CSC": "Workfront CSC",
    "Migration": "Workfront Migration",
}


def load_json_file(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_input_data(skill_matrix: Any = None, availability: Any = None):
    raw_skill = skill_matrix if skill_matrix is not None else load_json_file(SKILL_FILE)
    raw_avail = availability if availability is not None else load_json_file(AVAIL_FILE)
    return raw_skill, raw_avail


def normalize_skill_matrix(raw: Any) -> List[Dict[str, Any]]:
    if not isinstance(raw, list):
        raise ValueError("Skill matrix must be a list or omitted to use the data folder file.")

    people = []
    for row in raw:
        name = row.get("Name")
        details_list = row.get("details") or []
        details = details_list[0] if details_list else {}
        caps = {}
        for short, full in CAP_MAP.items():
            verdict_key = f"{short} Verdict"
            norm_key = f"Normalizing {short}" if short != "Core" else "Normalizing core"
            if short == "Planning":
                norm_key = "Normalizing Planning"
            elif short == "Migration":
                norm_key = "Normalizing Migration"
            elif short == "Fusion":
                norm_key = "Normalizing fusion"
            elif short == "CSC":
                norm_key = "Normalizing CSC"
            caps[full] = {
                "verdict": details.get(verdict_key, "Unknown"),
                "score": float(details.get(norm_key, 0) or 0),
            }

        people.append({
            "name": name,
            "capabilities": caps,
            "overall_strength": float(details.get("Overall Capability Strength", 0) or 0),
            "overall_verdict": details.get("Overall Verdict", "Unknown"),
            "overall_summary": details.get("Overall Summary", "Unknown"),
        })
    return people


def normalize_availability(raw: Any) -> Dict[str, Dict[str, Any]]:
    if not isinstance(raw, list):
        raise ValueError("Availability data must be a list or omitted to use the data folder file.")

    out = {}
    for row in raw:
        name = row.get("Resourse name") or row.get("Resource name") or row.get("name")
        if not name or name == "Grand Total":
            continue
        hours = row.get("hours") or []
        avg = round(sum(hours) / len(hours), 1) if hours else 0.0
        overload = any(h > 50 for h in hours)
        if avg <= 30:
            status = "Available"
            status_score = 1.0
            reason = "Low average workload"
        elif avg <= 40:
            status = "Partial"
            status_score = 0.65
            reason = "Moderate workload"
        else:
            status = "Unavailable"
            status_score = 0.25
            reason = "High workload"
        if overload and status == "Available":
            status = "Partial"
            status_score = 0.65
            reason = "Workload spikes detected"
        out[name.strip().lower()] = {
            "hours": hours,
            "avg_hours": avg,
            "overload": overload,
            "status": status,
            "status_score": status_score,
            "reason": reason,
        }
    return out
