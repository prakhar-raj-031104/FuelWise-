"""Ratings endpoints: submit a rating and read the aggregated summary."""

from fastapi import APIRouter

from app.agent.tools import find_dish
from app.schemas import RatingRequest, RatingSummaryResponse
from app.services import ratings_store

router = APIRouter()


@router.post("/ratings")
def submit_rating(request: RatingRequest) -> dict:
    # Normalise the dish name to the canonical menu spelling when possible,
    # matching the agent tool's behaviour so the dashboard groups cleanly.
    dish = find_dish(request.dish) or request.dish.strip().title()
    ratings_store.append_rating(dish, request.rating)
    return {"ok": True, "dish": dish, "rating": request.rating}


@router.get("/ratings/summary", response_model=RatingSummaryResponse)
def ratings_summary() -> RatingSummaryResponse:
    summary = ratings_store.summarize()
    return RatingSummaryResponse(**summary)
