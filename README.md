# IntelliMatch AI Chatbot (Dual Mode: `data/` fallback + HTTP payload)

This package adds a chatbot input layer **without changing your core usage pattern**.

It supports **both**:
1. **Manual testing** using files placed in the `data/` folder
2. **HTTP/Fusion execution** by sending `skill_matrix` and `availability` in the API payload

## Folder Structure

```text
intellimatch_chatbot_dual_mode/
├── app.py
├── engine.py
├── models.py
├── data_loader.py
├── streamlit_app.py
├── test_manual_chat.py
├── requirements.txt
└── data/
    ├── sample_skill_matrix.json
    └── availability.json
```

## Install

```bash
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app:app --reload --port 8002
```

## Health Check

```bash
http://localhost:8002/health
```

## Manual Test (API reads from `data/` folder)

```bash
python test_manual_chat.py --query "Need someone with Workfront Core and Planning who is available"
```

## Manual Test (send files in HTTP payload, same style as Fusion)

```bash
python test_manual_chat.py --query "Need someone with Workfront Core and Planning who is available" --send-http-data
```

## Fusion / HTTP Payload Example

```json
{
  "query": "Need someone with Workfront Core and Planning who is available immediately",
  "skill_matrix": [ ... your skill matrix JSON ... ],
  "availability": [ ... your availability JSON ... ],
  "top_k": 5
}
```

If `skill_matrix` or `availability` are **not** provided in the HTTP payload, the API automatically falls back to:
- `data/sample_skill_matrix.json`
- `data/availability.json`

## Streamlit UI

```bash
streamlit run streamlit_app.py
```

Open the UI at:

```bash
http://localhost:8501
```

The Streamlit UI calls the FastAPI backend at `http://localhost:8002`, so keep the API running in a separate terminal:

```bash
uvicorn app:app --reload --port 8002
```

This UI can:
- use local files from `data/`
- or send JSON directly to the API

## Notes

- This starter is intentionally designed to preserve your **existing architecture**:
  - FastAPI remains the backend
  - Fusion can still call via HTTP
  - Manual testing still works from local files
- The chatbot is only a **new input method**.
- You can plug your current LLM/SBERT/scoring pipeline into `engine.py` later if you want identical scoring behavior.
