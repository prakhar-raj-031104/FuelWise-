import { useEffect, useState } from "react";
import { ChatWindow } from "./components/ChatWindow";
import { MenuView } from "./components/MenuView";
import { RatingsDashboard } from "./components/RatingsDashboard";
import { getHealth } from "./api/client";

type Tab = "chat" | "menu" | "ratings";

const TAB_LABELS: Record<Tab, string> = { chat: "Chat", menu: "Menu", ratings: "Ratings" };

export default function App() {
  const [tab, setTab] = useState<Tab>("chat");
  const [ready, setReady] = useState<boolean | null>(null);

  useEffect(() => {
    getHealth()
      .then((h) => setReady(h.ollama_reachable && h.model_present))
      .catch(() => setReady(false));
  }, []);

  const ollamaDown = ready === false;

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <span className="logo">🍽️</span>
          <div>
            <h1>FuelWise</h1>
            <p className="tagline">Smart mess-food decisions for hostel life</p>
            {ready !== null && (
              <span className={`status-dot ${ollamaDown ? "down" : ""}`}>
                {ollamaDown ? "AI offline" : "AI ready"}
              </span>
            )}
          </div>
        </div>
        <nav className="tabs">
          {(["chat", "menu", "ratings"] as Tab[]).map((t) => (
            <button key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>
              {TAB_LABELS[t]}
            </button>
          ))}
        </nav>
      </header>

      {ollamaDown && tab === "chat" && (
        <div className="warning-banner">
          The local AI model isn't ready, so chat won't work yet. Make sure Ollama is running and
          the model is pulled. Menu and Ratings still work.
        </div>
      )}

      <main className="app-main">
        {tab === "chat" && <ChatWindow />}
        {tab === "menu" && <MenuView />}
        {tab === "ratings" && <RatingsDashboard />}
      </main>
    </div>
  );
}
