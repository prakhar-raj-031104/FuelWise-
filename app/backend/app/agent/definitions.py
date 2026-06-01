"""Ollama tool/function definitions for FuelWise.

Moved verbatim from the original CLI. These are passed to Ollama's /api/chat so
the model knows which tools it may call.
"""

from typing import Any


def prop(prop_type: str, description: str, **extra: Any) -> dict[str, Any]:
    return {"type": prop_type, "description": description, **extra}


def tool(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


TOOL_DEFINITIONS = [
    tool(
        "get_today_menu",
        "Get today's mess menu for breakfast, lunch, snacks, dinner, or all meals.",
        {"meal": prop("string", "Meal name: breakfast, lunch, snacks, dinner, or all.")},
        ["meal"],
    ),
    tool(
        "get_nutrition",
        "Get calories, macros, allergens, and a practical note for a dish.",
        {"dish": prop("string", "Dish name from the menu.")},
        ["dish"],
    ),
    tool(
        "check_user_goals",
        "Get meal-planning rules for bulk, cut, or maintain goals.",
        {"goal": prop("string", "Fitness goal, e.g. bulk, cut, maintain, gain muscle, or lose fat.")},
        ["goal"],
    ),
    tool(
        "suggest_outside_alternative",
        "Suggest outside food alternatives based on craving and budget.",
        {
            "craving": prop("string", "Craving, e.g. protein, spicy, sweet, chicken, vegetarian."),
            "budget": prop("integer", "Maximum budget in rupees."),
        },
        ["craving", "budget"],
    ),
    tool(
        "log_meal_rating",
        "Log a student's rating for a mess dish from 1 to 5.",
        {
            "dish": prop("string", "Dish being rated."),
            "rating": prop("integer", "Rating from 1 to 5.", minimum=1, maximum=5),
        },
        ["dish", "rating"],
    ),
]
