import re
import os
from functools import lru_cache
from typing import Any, Dict, List
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from data_loader import get_input_data, normalize_skill_matrix, normalize_availability

# Set HuggingFace cache directory to local project directory
CACHE_DIR = Path(__file__).resolve().parent / ".model_cache"
os.environ["HF_HOME"] = str(CACHE_DIR)
os.environ["TRANSFORMERS_CACHE"] = str(CACHE_DIR)

CAPABILITY_ALIASES = {
    "workfront core": "Workfront Core",
    "core": "Workfront Core",
    "planning": "Workfront Planning",
    "workfront planning": "Workfront Planning",
    "fusion": "Workfront Fusion",
    "workfront fusion": "Workfront Fusion",
    "csc": "Workfront CSC",
    "workfront csc": "Workfront CSC",
    "migration": "Workfront Migration",
    "workfront migration": "Workfront Migration",
}
ALL_CAPS = [
    "Workfront Core",
    "Workfront Planning",
    "Workfront Fusion",
    "Workfront CSC",
    "Workfront Migration",
]

@lru_cache(maxsize=1)
def get_model():
    try:
        # Try to load from local cache first, then download if needed
        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            cache_folder=str(CACHE_DIR),
            device='cpu'  # Use CPU to avoid GPU memory issues
        )
        return model
    except Exception as e:
        print(f"Warning: Could not load SentenceTransformer model: {e}")
        print("Make sure you have internet connection for first-time model download.")
        raise


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return float(np.dot(a, b) / denom)


def extract_requested_caps(query: str) -> List[str]:
    q = query.lower()
    caps = []
    for alias, full in CAPABILITY_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", q) and full not in caps:
            caps.append(full)
    # If user doesn't mention a specific capability, compare across all
    return caps if caps else ALL_CAPS[:]


def build_candidate_cap_text(person: Dict[str, Any], caps: List[str]) -> Dict[str, str]:
    out = {}
    for cap in caps:
        cap_data = person["capabilities"].get(cap, {})
        verdict = cap_data.get("verdict", "Unknown")
        score = cap_data.get("score", 0)
        text = f"{cap} {verdict} capability score {score}"
        out[cap] = text
    return out


def coverage_score(person: Dict[str, Any], requested_caps: List[str]) -> float:
    if not requested_caps:
        return 0.0
    present = 0
    for cap in requested_caps:
        if person["capabilities"].get(cap, {}).get("score", 0) > 0:
            present += 1
    return present / len(requested_caps)


def capability_reason(breakdown: Dict[str, float]) -> str:
    if not breakdown:
        return "No capability data"
    sorted_items = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
    top_val = sorted_items[0][1] if sorted_items else 0.0
    strong, moderate, low = [], [], []
    for cap, val in sorted_items:
        ratio = val / top_val if top_val > 0 else 0.0
        if val >= 0.6:
            strong.append(cap)
        elif val >= 0.4:
            moderate.append(cap)
        elif ratio >= 0.8:
            moderate.append(cap)
        else:
            low.append(cap)
    parts = []
    if strong:
        parts.append("Strong: " + ", ".join(strong))
    if moderate:
        parts.append("Moderate: " + ", ".join(moderate))
    if low:
        parts.append("Low: " + ", ".join(low))
    return " | ".join(parts)


def run_chat_matching(query: str, skill_matrix: Any = None, availability: Any = None, top_k: int = 5):
    raw_skill, raw_avail = get_input_data(skill_matrix, availability)
    people = normalize_skill_matrix(raw_skill)
    avail_map = normalize_availability(raw_avail)
    requested_caps = extract_requested_caps(query)

    model = get_model()
    query_emb = model.encode(query)

    max_strength = max((p.get("overall_strength", 0) for p in people), default=1.0) or 1.0
    results = []

    for person in people:
        cap_texts = build_candidate_cap_text(person, requested_caps)
        breakdown = {}
        weighted_semantic = 0.0
        weights = []
        cap_weights = []

        # Use equal weights for chatbot requests unless you later plug in LLM-generated weights.
        if requested_caps:
            cap_weights = [1 / len(requested_caps)] * len(requested_caps)
        else:
            cap_weights = []

        for i, cap in enumerate(requested_caps):
            emb = model.encode(cap_texts[cap])
            sim = max(0.0, cosine_sim(query_emb, emb))
            contribution = sim * cap_weights[i]
            breakdown[cap] = round(contribution, 4)
            weighted_semantic += contribution
            weights.append(sim)

        strength = person.get("overall_strength", 0.0)
        strength_norm = strength / max_strength if max_strength > 0 else 0.0
        coverage = coverage_score(person, requested_caps)

        a = avail_map.get(person["name"].strip().lower(), {
            "status": "Unknown",
            "status_score": 0.5,
            "avg_hours": None,
            "reason": "No availability data found",
            "overload": False,
        })
        avail_score = a.get("status_score", 0.5)

        final_score = round((0.60 * weighted_semantic) + (0.25 * strength_norm) + (0.10 * coverage) + (0.05 * avail_score), 4)

        if final_score >= 0.65:
            quality = "Excellent Match"
        elif final_score >= 0.55:
            quality = "High"
        elif final_score >= 0.45:
            quality = "Moderate"
        else:
            quality = "Low"

        results.append({
            "name": person["name"],
            "overall_strength": round(strength, 2),
            "overall_verdict": person.get("overall_verdict"),
            "semantic_weighted": round(weighted_semantic, 4),
            "coverage": round(coverage, 4),
            "availability_status": a.get("status"),
            "availability_avg_hours": a.get("avg_hours"),
            "availability_reason": a.get("reason"),
            "availability_overload": a.get("overload"),
            "match_quality": quality,
            "match_reason": capability_reason(breakdown),
            "breakdown": breakdown,
            "final_score": final_score,
        })

    results = sorted(results, key=lambda x: x["final_score"], reverse=True)[:top_k]
    return {
        "query": query,
        "requested_capabilities": requested_caps,
        "top_k": top_k,
        "results": results,
        "data_source": {
            "skill_matrix": "http_payload" if skill_matrix is not None else "data/sample_skill_matrix.json",
            "availability": "http_payload" if availability is not None else "data/availability.json",
        },
    }
