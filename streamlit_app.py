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

with st.form("match_form"):
    st.subheader("Enter your project requirement")
    st.write("Describe the role, capabilities, and availability you need in plain language.")
    query = st.text_area(
        "Project requirement",
        value="Need someone with Workfront Core and Planning who is available",
        height=140,
        help="Example: Need someone with Workfront Core and Planning who can join a project immediately."
    )
    top_k = st.slider(
        "Number of candidates to show",
        1,
        10,
        5,
        help="Choose how many top matches you want returned."
    )
    use_local = st.checkbox(
        "Use local data folder files",
        value=True,
        help="Use the built-in sample data if checked; otherwise paste JSON payloads."
    )

    if not use_local:
        with st.expander("Paste skill matrix JSON"):
            skill_json = st.text_area("Skill Matrix JSON", height=180)
        with st.expander("Paste availability JSON"):
            availability_json = st.text_area("Availability JSON", height=120)
    else:
        skill_json = ""
        availability_json = ""

    submit = st.form_submit_button("Find Candidates")

if submit:
    payload = {"query": query, "top_k": top_k}
    if not use_local:
        if skill_json.strip():
            payload["skill_matrix"] = json.loads(skill_json)
        if availability_json.strip():
            payload["availability"] = json.loads(availability_json)

    with st.spinner("Finding the best matches for your request..."):
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
