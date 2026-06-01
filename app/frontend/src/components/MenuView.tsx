import { useEffect, useState } from "react";
import { getMenu, type MenuResponse } from "../api/client";

const MEALS: { key: string; label: string; emoji: string }[] = [
  { key: "breakfast", label: "Breakfast", emoji: "🌅" },
  { key: "lunch", label: "Lunch", emoji: "☀️" },
  { key: "snacks", label: "Snacks", emoji: "🍵" },
  { key: "dinner", label: "Dinner", emoji: "🌙" },
];

export function MenuView() {
  const [data, setData] = useState<MenuResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMenu().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <div className="loading">Loading menu…</div>;

  const days = Object.keys(data.menu);

  return (
    <div className="scroll-area">
      <div className="section-head">
        <h2>Weekly Mess Menu</h2>
        <span className="muted">Today is {data.today}</span>
      </div>
      <div className="menu-grid">
        {days.map((day) => (
          <div key={day} className={`day-card ${day === data.today ? "today" : ""}`}>
            <div className="day-card-head">
              <h3>{day}</h3>
              {day === data.today && <span className="today-tag">TODAY</span>}
            </div>
            {MEALS.map((meal) => (
              <div key={meal.key} className="meal-row">
                <div className="meal-label">
                  <span>{meal.emoji}</span> {meal.label}
                </div>
                <div className="meal-items">{data.menu[day][meal.key]?.join(", ")}</div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
