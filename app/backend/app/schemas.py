"""Pydantic request/response models for the API."""

from typing import Any, Optional

from pydantic import BaseModel, Field


# ===== Chat =====

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's message to FuelWise.")
    session_id: Optional[str] = Field(None, description="Existing session id; omit to start a new chat.")


class TraceEntry(BaseModel):
    tool: str
    args: dict[str, Any]
    result: str


class ChatResponse(BaseModel):
    reply: str
    trace: list[TraceEntry]
    session_id: str


# ===== Ratings =====

class RatingRequest(BaseModel):
    dish: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)


class RatingSummaryItem(BaseModel):
    dish: str
    count: int
    average: float
    last_rated: str


class RatingSummaryResponse(BaseModel):
    items: list[RatingSummaryItem]
    total_ratings: int


# ===== Health =====

class HealthResponse(BaseModel):
    status: str
    ollama_reachable: bool
    model_present: bool
    model: str
