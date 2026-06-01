"""FuelWise tool implementations.

Moved verbatim from the original CLI. Pure functions over the static data plus
the JSONL rating log. The ratings write path is delegated to the ratings_store
service so the web app and CLI share one storage format.
"""

from datetime import date, datetime
from difflib import get_close_matches
from typing import Any, Optional

from app.agent.data import (
    ALL_DISHES,
    GOAL_GUIDES,
    NUTRITION_DB,
    OUTSIDE_OPTIONS,
    WEEKLY_MENU,
)


def normalise(text: str) -> str:
    return text.strip().lower().replace("_", " ").replace("-", " ")


def find_dish(dish: str) -> Optional[str]:
    wanted = normalise(dish)
    for known_dish in ALL_DISHES:
        if normalise(known_dish) == wanted:
            return known_dish
    matches = get_close_matches(dish, ALL_DISHES, n=1, cutoff=0.65)
    return matches[0] if matches else None


# ===== Tool Implementations =====

def get_today_menu(meal: str) -> str:
    day = date.today().strftime("%A")
    day_menu = WEEKLY_MENU[day]
    meal_key = normalise(meal)

    if meal_key in {"all", "full day", "today", "day"}:
        meals = day_menu.keys()
    elif meal_key in day_menu:
        meals = [meal_key]
    else:
        return f"Unknown meal '{meal}'. Try breakfast, lunch, snacks, dinner, or all."

    lines = [f"{day} mess menu:"]
    lines.extend(f"- {name.title()}: {', '.join(day_menu[name])}" for name in meals)
    return "\n".join(lines)


def get_nutrition(dish: str) -> str:
    matched = find_dish(dish)
    if not matched or matched not in NUTRITION_DB:
        suggestions = ", ".join(get_close_matches(dish, ALL_DISHES, n=3, cutoff=0.35))
        hint = f" Did you mean: {suggestions}?" if suggestions else ""
        return f"No nutrition data found for '{dish}'.{hint}"

    info = NUTRITION_DB[matched]
    allergens = ", ".join(info["allergens"]) if info["allergens"] else "none listed"
    return (
        f"{matched}: {info['calories']} kcal, {info['protein']}g protein, "
        f"{info['carbs']}g carbs, {info['fat']}g fat. "
        f"Allergens: {allergens}. Note: {info['note']}"
    )


def check_user_goals(goal: str) -> str:
    text = normalise(goal)
    if any(word in text for word in ["bulk", "gain", "muscle", "surplus"]):
        resolved = "bulk"
    elif any(word in text for word in ["cut", "fat loss", "lose", "deficit", "weight loss"]):
        resolved = "cut"
    elif any(word in text for word in ["maintain", "maintenance", "balanced", "normal"]):
        resolved = "maintain"
    else:
        return "Goal not recognized. Use one of: bulk, cut, maintain."

    summary, plate_rule, strategy, limit = GOAL_GUIDES[resolved]
    return f"Goal: {resolved}. {summary} Plate rule: {plate_rule} Mess strategy: {strategy} Limit: {limit}"


def suggest_outside_alternative(craving: str, budget: int) -> str:
    try:
        budget = int(budget)
    except (TypeError, ValueError):
        return "Budget must be a number in rupees."

    craving_words = set(normalise(craving).split())
    affordable = [item for item in OUTSIDE_OPTIONS if item["price"] <= budget]
    if not affordable:
        return f"No outside options under Rs {budget}. Fallback: banana, curd, or sprouts from the mess."

    def score(item: dict[str, Any]) -> tuple[int, int]:
        return (len(item["tags"] & craving_words), -item["price"])

    top = sorted(affordable, key=score, reverse=True)[:3]
    lines = [f"Best outside alternatives under Rs {budget} for '{craving}':"]
    lines.extend(f"- {item['name']} - Rs {item['price']}: {item['reason']}" for item in top)
    return "\n".join(lines)


def log_meal_rating(dish: str, rating: int) -> str:
    # Imported lazily to avoid a circular import (ratings_store imports config,
    # which has no dependency back on tools, but keeping it local is cleaner).
    from app.services.ratings_store import append_rating

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return "Rating must be a number from 1 to 5."
    if rating < 1 or rating > 5:
        return "Rating must be between 1 and 5."

    matched = find_dish(dish) or dish.strip().title()
    append_rating(matched, rating)
    return f"Logged {rating}/5 for {matched}. Thanks - the mess memory got sharper."


TOOL_FUNCTIONS = {
    "get_today_menu": get_today_menu,
    "get_nutrition": get_nutrition,
    "check_user_goals": check_user_goals,
    "suggest_outside_alternative": suggest_outside_alternative,
    "log_meal_rating": log_meal_rating,
}
