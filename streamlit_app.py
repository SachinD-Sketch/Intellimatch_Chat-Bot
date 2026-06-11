import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


API_URL = "http://localhost:8002"

st.set_page_config(page_title="IntelliMatch AI Chatbot", layout="wide")
st.title("IntelliMatch AI Chatbot")
st.caption("Uses local data files for manual testing while the API also supports HTTP payloads from Fusion.")

data_dir = Path(__file__).resolve().parent / "data"

with st.sidebar:
    st.header("Backend")
    st.code(API_URL)
    try:
        health = requests.get(f"{API_URL}/health", timeout=3)
        health.raise_for_status()
        st.success("API connected")
    except Exception:
        st.warning("Start the API with: uvicorn app:app --reload --port 8002")

query = st.text_input("Enter project requirement", "Need someone with Workfront Core and Planning who is available")
top_k = st.slider("Top K", 1, 10, 5)
use_local = st.checkbox("Use local data folder files", value=True)

payload = {"query": query, "top_k": top_k}
if not use_local:
    skill_json = st.text_area("Skill Matrix JSON")
    availability_json = st.text_area("Availability JSON")
    if skill_json.strip():
        payload["skill_matrix"] = json.loads(skill_json)
    if availability_json.strip():
        payload["availability"] = json.loads(availability_json)

if st.button("Find Candidates"):
    try:
        response = requests.post(f"{API_URL}/chat", json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        st.success(f"Requested capabilities: {', '.join(data.get('requested_capabilities', []))}")

        df = pd.DataFrame(data.get("results", []))
        if not df.empty:
            st.dataframe(
                df[
                    [
                        "name",
                        "final_score",
                        "match_quality",
                        "availability_status",
                        "overall_strength",
                        "semantic_weighted",
                    ]
                ],
                width='stretch',
            )
            st.bar_chart(df.set_index("name")["final_score"])
            for row in data["results"]:
                with st.expander(f"{row['name']} - {row['match_quality']}"):
                    st.write("**Match reason:**", row["match_reason"])
                    st.write("**Availability:**", row["availability_status"], "-", row["availability_reason"])
                    st.json(row["breakdown"])
        else:
            st.warning("No results returned")
    except Exception as exc:
        st.error(str(exc))
