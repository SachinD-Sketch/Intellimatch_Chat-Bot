from fastapi import FastAPI, HTTPException
from models import ChatRequest
from engine import run_chat_matching

app = FastAPI(title="IntelliMatch AI Chatbot API", version="1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        return run_chat_matching(
            query=req.query,
            skill_matrix=req.skill_matrix,
            availability=req.availability,
            top_k=req.top_k,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
