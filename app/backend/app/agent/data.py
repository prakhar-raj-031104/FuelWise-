"""Static food domain data for FuelWise.

Moved verbatim from the original mess_menu_agent.py CLI. This is the reusable
core: the weekly menu, nutrition database, goal guides, and outside options.
"""

from typing import Any


WEEKLY_MENU = {
    "Monday": {
        "breakfast": ["Poha", "Boiled Eggs", "Banana", "Tea"],
        "lunch": ["Dal Tadka", "Jeera Rice", "Roti", "Aloo Gobi", "Curd"],
        "snacks": ["Samosa", "Green Chutney", "Tea"],
        "dinner": ["Paneer Curry", "Roti", "Rice", "Cucumber Salad"],
    },
    "Tuesday": {
        "breakfast": ["Idli Sambar", "Coconut Chutney", "Banana", "Tea"],
        "lunch": ["Rajma", "Rice", "Roti", "Mixed Veg", "Curd"],
        "snacks": ["Veg Sandwich", "Tea"],
        "dinner": ["Egg Curry", "Roti", "Rice", "Onion Salad"],
    },
    "Wednesday": {
        "breakfast": ["Aloo Paratha", "Curd", "Pickle", "Tea"],
        "lunch": ["Chole", "Rice", "Roti", "Bhindi Fry", "Salad"],
        "snacks": ["Maggi", "Tea"],
        "dinner": ["Dal Fry", "Veg Pulao", "Roti", "Sprouts Salad"],
    },
    "Thursday": {
        "breakfast": ["Upma", "Boiled Eggs", "Banana", "Tea"],
        "lunch": ["Kadhi", "Rice", "Roti", "Beans Poriyal", "Curd"],
        "snacks": ["Pakora", "Tea"],
        "dinner": ["Chicken Curry", "Roti", "Rice", "Cucumber Salad"],
    },
    "Friday": {
        "breakfast": ["Dosa", "Sambar", "Coconut Chutney", "Tea"],
        "lunch": ["Dal Makhani", "Rice", "Roti", "Aloo Jeera", "Curd"],
        "snacks": ["Sprouts Chaat", "Tea"],
        "dinner": ["Paneer Bhurji", "Roti", "Rice", "Salad"],
    },
    "Saturday": {
        "breakfast": ["Bread Omelette", "Banana", "Tea"],
        "lunch": ["Veg Pulao", "Raita", "Roti", "Chana Masala"],
        "snacks": ["Pav Bhaji", "Tea"],
        "dinner": ["Dal Tadka", "Rice", "Roti", "Aloo Gobi", "Curd"],
    },
    "Sunday": {
        "breakfast": ["Poori Sabzi", "Tea"],
        "lunch": ["Chicken Biryani", "Veg Biryani", "Raita", "Salad"],
        "snacks": ["Cold Coffee", "Veg Sandwich"],
        "dinner": ["Khichdi", "Curd", "Papad", "Pickle"],
    },
}


def nutrition(calories: int, protein: int, carbs: int, fat: int, allergens: str, note: str) -> dict[str, Any]:
    return {
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "allergens": allergens.split() if allergens else [],
        "note": note,
    }


NUTRITION_DB = {
    "Poha": nutrition(260, 6, 42, 8, "peanut", "Light breakfast; add eggs or curd for protein."),
    "Boiled Eggs": nutrition(156, 13, 1, 11, "egg", "High-quality protein; useful for bulking or cutting."),
    "Banana": nutrition(105, 1, 27, 0, "", "Good quick carbs before class, gym, or sports."),
    "Tea": nutrition(70, 2, 10, 2, "milk", "Fine in moderation; sugar adds up quickly."),
    "Dal Tadka": nutrition(220, 12, 28, 7, "", "Reliable vegetarian protein base."),
    "Jeera Rice": nutrition(260, 5, 52, 4, "", "Easy carbs; portion size decides whether it fits a cut."),
    "Rice": nutrition(240, 4, 52, 1, "", "Simple carb source; pair with dal, egg, paneer, or chicken."),
    "Roti": nutrition(110, 3, 22, 2, "gluten", "Good controlled carb option."),
    "Aloo Gobi": nutrition(180, 4, 24, 8, "", "Decent vegetables, but not a protein source."),
    "Curd": nutrition(90, 5, 7, 4, "milk", "Good add-on for gut comfort and extra protein."),
    "Samosa": nutrition(280, 5, 34, 14, "gluten", "Tasty, but fried; limit during a cut."),
    "Green Chutney": nutrition(20, 1, 3, 1, "", "Mostly flavor; check spice tolerance."),
    "Paneer Curry": nutrition(320, 16, 12, 24, "milk", "Protein-rich but calorie dense."),
    "Cucumber Salad": nutrition(30, 1, 6, 0, "", "Great volume food; helps with fullness."),
    "Idli Sambar": nutrition(280, 10, 54, 3, "", "Light and balanced; sambar improves protein and fiber."),
    "Coconut Chutney": nutrition(110, 2, 5, 9, "coconut", "Calorie dense for a small serving."),
    "Rajma": nutrition(260, 14, 42, 4, "", "Strong vegetarian protein and fiber option."),
    "Mixed Veg": nutrition(140, 4, 18, 6, "", "Useful micronutrients; pair with protein."),
    "Veg Sandwich": nutrition(240, 8, 38, 6, "gluten", "Better snack than fried options."),
    "Egg Curry": nutrition(300, 18, 10, 20, "egg", "Great protein; watch gravy oil."),
    "Onion Salad": nutrition(35, 1, 8, 0, "", "Good crunch and volume."),
    "Aloo Paratha": nutrition(330, 8, 48, 12, "gluten", "Heavy breakfast; balance with curd and lighter lunch."),
    "Pickle": nutrition(25, 0, 2, 2, "", "High sodium; keep it small."),
    "Chole": nutrition(280, 13, 44, 6, "", "Good fiber and vegetarian protein."),
    "Bhindi Fry": nutrition(180, 4, 16, 11, "", "Vegetable option, often oil-heavy."),
    "Salad": nutrition(40, 1, 8, 0, "", "Easy way to improve fullness."),
    "Maggi": nutrition(360, 8, 52, 14, "gluten", "Comfort food; low satiety for the calories."),
    "Dal Fry": nutrition(240, 12, 30, 8, "", "Useful protein base, but oil can vary."),
    "Veg Pulao": nutrition(300, 7, 55, 7, "", "Good carb source; needs protein alongside."),
    "Sprouts Salad": nutrition(120, 9, 18, 2, "", "Excellent high-fiber snack or dinner add-on."),
    "Upma": nutrition(290, 7, 46, 9, "gluten", "Decent breakfast; add eggs for protein."),
    "Kadhi": nutrition(190, 8, 18, 9, "milk", "Comforting but not very high in protein."),
    "Beans Poriyal": nutrition(120, 4, 14, 5, "coconut", "Good vegetable side."),
    "Pakora": nutrition(310, 7, 32, 17, "", "Fried snack; best treated as occasional."),
    "Chicken Curry": nutrition(360, 28, 8, 24, "", "Best mess protein option when available."),
    "Dosa": nutrition(220, 6, 38, 5, "", "Light carb base; pair with sambar."),
    "Sambar": nutrition(140, 7, 22, 3, "", "Adds protein and fiber to South Indian breakfast."),
    "Dal Makhani": nutrition(330, 15, 34, 16, "milk", "Good protein, but richer than regular dal."),
    "Aloo Jeera": nutrition(210, 4, 30, 9, "", "Carb-heavy side."),
    "Sprouts Chaat": nutrition(160, 10, 24, 3, "", "One of the better mess snacks."),
    "Paneer Bhurji": nutrition(340, 18, 10, 25, "milk", "High protein, high fat; portion control matters."),
    "Bread Omelette": nutrition(360, 18, 38, 15, "egg gluten", "Solid breakfast for busy mornings."),
    "Raita": nutrition(110, 5, 10, 5, "milk", "Cooling side; adds some protein."),
    "Chana Masala": nutrition(300, 14, 46, 7, "", "Strong vegetarian protein and fiber."),
    "Pav Bhaji": nutrition(420, 10, 62, 15, "gluten milk", "Fun snack but calorie-heavy."),
    "Poori Sabzi": nutrition(450, 8, 58, 22, "gluten", "Weekend treat; avoid stacking with a heavy lunch."),
    "Chicken Biryani": nutrition(620, 30, 72, 24, "", "Good protein but calorie dense."),
    "Veg Biryani": nutrition(520, 12, 78, 18, "", "High-energy meal; add curd or sprouts if available."),
    "Cold Coffee": nutrition(240, 7, 34, 8, "milk", "Sugar-heavy drink; can replace, not accompany, a snack."),
    "Khichdi": nutrition(300, 11, 52, 6, "", "Easy dinner when digestion or workload is rough."),
    "Papad": nutrition(55, 2, 8, 2, "", "Crunchy side; can be salty."),
}


GOAL_GUIDES = {
    "bulk": (
        "Eat a calorie surplus with enough protein.",
        "Choose 1 protein anchor, 2 carb servings, vegetables, and curd if tolerated.",
        "Prefer eggs, paneer, chicken, dal, rajma, chole, curd, rice, and roti.",
        "Do not fill up only on fried snacks; they add calories without enough protein.",
    ),
    "cut": (
        "Eat high protein with controlled calories.",
        "Choose 1 protein anchor, 1 carb serving, and a large salad or vegetable side.",
        "Prefer eggs, dal, chicken, sprouts, curd, salad, and smaller rice/roti portions.",
        "Limit samosa, pakora, poori, Maggi, biryani, sweet drinks, and extra gravy.",
    ),
    "maintain": (
        "Keep energy steady without overthinking every meal.",
        "Choose 1 protein anchor, 1 to 2 carb servings, and vegetables.",
        "Build a balanced plate and adjust portions around gym, sports, and class load.",
        "Avoid turning every snack into a fried snack plus sugary tea combo.",
    ),
}


def outside_option(name: str, price: int, tags: str, reason: str) -> dict[str, Any]:
    return {"name": name, "price": price, "tags": set(tags.split()), "reason": reason}


OUTSIDE_OPTIONS = [
    outside_option("Egg bhurji with 2 rotis", 80, "protein spicy egg bulk cut", "High protein, filling, and usually available near campus."),
    outside_option("Chicken roll without mayo", 120, "protein chicken spicy bulk maintain", "Good protein when mess dinner is weak; skip mayo to control calories."),
    outside_option("Paneer roll with extra salad", 110, "protein paneer vegetarian bulk maintain", "Vegetarian protein option; extra salad improves fullness."),
    outside_option("Curd bowl with banana", 60, "sweet light vegetarian maintain cut", "Simple, cheap, and better than a sugary drink plus fried snack."),
    outside_option("Sprouts chaat", 50, "protein light vegetarian cut", "Best budget pick for protein, fiber, and fullness."),
    outside_option("Tandoori chicken half plate", 180, "protein chicken gym bulk cut", "Lean protein if you avoid creamy dips and extra butter."),
    outside_option("Masala dosa with sambar", 90, "south indian vegetarian maintain", "Comforting meal with a better balance than fried fast food."),
    outside_option("Milk plus peanut chikki", 45, "sweet budget bulk snack", "Cheap calories for bulking; avoid if peanut or milk allergy applies."),
]


ALL_DISHES = sorted(
    set(NUTRITION_DB) | {dish for daily_menu in WEEKLY_MENU.values() for dishes in daily_menu.values() for dish in dishes}
)
