from typing import Any, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., description="Natural language requirement")
    skill_matrix: Optional[Any] = Field(None, description="Optional skill matrix JSON. If omitted, loads data/sample_skill_matrix.json")
    availability: Optional[Any] = Field(None, description="Optional availability JSON. If omitted, loads data/availability.json")
    top_k: int = Field(5, ge=1, le=20)
