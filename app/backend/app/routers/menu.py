"""Menu endpoints: full weekly menu and today's menu."""

from datetime import date

from fastapi import APIRouter

from app.agent.data import WEEKLY_MENU

router = APIRouter()


@router.get("/menu")
def get_menu() -> dict:
    """Full weekly menu, with the current day flagged."""
    return {"today": date.today().strftime("%A"), "menu": WEEKLY_MENU}


@router.get("/menu/today")
def get_today() -> dict:
    day = date.today().strftime("%A")
    return {"day": day, "meals": WEEKLY_MENU[day]}
