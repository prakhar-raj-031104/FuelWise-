import { useEffect, useState } from "react";
import {
  getMenu,
  getRatingsSummary,
  submitRating,
  type RatingSummaryResponse,
} from "../api/client";

function Stars({ value }: { value: number }) {
  const full = Math.round(value);
  return <span className="rank-stars">{"★".repeat(full)}{"☆".repeat(5 - full)}</span>;
}

export function RatingsDashboard() {
  const [summary, setSummary] = useState<RatingSummaryResponse | null>(null);
  const [dishes, setDishes] = useState<string[]>([]);
  const [dish, setDish] = useState("");
  const [rating, setRating] = useState(5);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function refresh() {
    try {
      setSummary(await getRatingsSummary());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load ratings.");
    }
  }

  useEffect(() => {
    refresh();
    getMenu()
      .then((m) => {
        const all = new Set<string>();
        Object.values(m.menu).forEach((day) =>
          Object.values(day).forEach((items) => items.forEach((d) => all.add(d)))
        );
        const sorted = [...all].sort();
        setDishes(sorted);
        setDish(sorted[0] ?? "");
      })
      .catch(() => {});
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setNotice(null);
    try {
      await submitRating(dish, rating);
      setNotice(`Logged ${rating}★ for ${dish}.`);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit rating.");
    }
  }

  return (
    <div className="scroll-area">
      <div className="section-head">
        <h2>Dish Ratings</h2>
        {summary && <span className="muted">{summary.total_ratings} total ratings</span>}
      </div>

      <form className="rating-form" onSubmit={onSubmit}>
        <select value={dish} onChange={(e) => setDish(e.target.value)}>
          {dishes.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
        <select value={rating} onChange={(e) => setRating(Number(e.target.value))}>
          {[5, 4, 3, 2, 1].map((n) => (
            <option key={n} value={n}>{n} ★</option>
          ))}
        </select>
        <button type="submit" className="btn-primary" disabled={!dish}>
          Submit
        </button>
      </form>

      {notice && <div className="notice-banner">{notice}</div>}
      {error && <div className="error-banner">{error}</div>}

      {summary && summary.items.length === 0 && (
        <p className="muted" style={{ textAlign: "center", marginTop: 24 }}>
          No ratings yet — be the first to rate a dish! ⭐
        </p>
      )}

      {summary && summary.items.length > 0 && (
        <div className="leaderboard">
          {summary.items.map((item, i) => (
            <div key={item.dish} className="rank-card">
              <div className="rank-num">{i === 0 ? "🏆" : `#${i + 1}`}</div>
              <div>
                <div className="rank-dish">{item.dish}</div>
                <div className="rank-meta">
                  {item.count} rating{item.count > 1 ? "s" : ""}
                  {item.last_rated && ` · last ${item.last_rated.slice(0, 10)}`}
                </div>
                <div className="rank-bar">
                  <div style={{ width: `${(item.average / 5) * 100}%` }} />
                </div>
              </div>
              <div className="rank-score">
                <Stars value={item.average} />
                <div className="rank-avg">{item.average.toFixed(2)} / 5</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
