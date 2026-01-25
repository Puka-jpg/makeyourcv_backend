from typing import Optional

from pydantic import BaseModel

from adk.state import GraphState


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    state: Optional[GraphState] = None
