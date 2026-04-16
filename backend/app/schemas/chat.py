from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gemma2-9b-it"
    rep_id: str = "rep_001"


class ChatResponse(BaseModel):
    messages: List[Dict[str, Any]]
