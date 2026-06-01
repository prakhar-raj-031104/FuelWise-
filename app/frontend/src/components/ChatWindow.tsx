import { useEffect, useRef, useState } from "react";
import { streamChat, type TraceEntry } from "../api/client";
import { MessageBubble, type ChatMessage } from "./MessageBubble";

const EXAMPLES = [
  { emoji: "🥗", text: "I am cutting. What should I eat for dinner today?" },
  { emoji: "💪", text: "I want high protein food under Rs 120. What should I order?" },
  { emoji: "🥜", text: "I have a peanut allergy. Is today's breakfast safe?" },
  { emoji: "⭐", text: "Log Paneer Curry as 4 out of 5." },
];

export function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    setError(null);
    setInput("");
    // Append the user message and an empty assistant message we'll stream into.
    setMessages((prev) => [
      ...prev,
      { role: "user", content: trimmed },
      { role: "assistant", content: "", trace: [] },
    ]);
    setLoading(true);

    const trace: TraceEntry[] = [];
    let answer = "";
    let streamError: string | null = null;

    // Update the last (assistant) message in place as events arrive.
    const updateLast = (patch: Partial<ChatMessage>) =>
      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = { ...next[next.length - 1], ...patch };
        return next;
      });

    try {
      await streamChat(trimmed, sessionId, (event) => {
        switch (event.type) {
          case "session":
            setSessionId(event.session_id);
            break;
          case "tool":
            trace.push({ tool: event.tool, args: event.args, result: event.result });
            updateLast({ trace: [...trace] });
            break;
          case "token":
            answer += event.text;
            updateLast({ content: answer });
            break;
          case "error":
            streamError = event.detail;
            break;
        }
      });
    } catch (e) {
      streamError = e instanceof Error ? e.message : "Something went wrong.";
    } finally {
      setLoading(false);
    }

    if (streamError) {
      setError(streamError);
      // Drop the empty assistant placeholder if nothing was generated.
      if (!answer) setMessages((prev) => prev.slice(0, -1));
    }
  }

  return (
    <div className="chat">
      <div className="messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🍽️</div>
            <h2>What should you eat today?</h2>
            <p>Ask FuelWise about the menu, your fitness goal, allergies, cravings, or ratings.</p>
            <div className="examples">
              {EXAMPLES.map((ex) => (
                <button key={ex.text} className="example-chip" onClick={() => send(ex.text)}>
                  <span className="e-emoji">{ex.emoji}</span>
                  {ex.text}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {error && <div className="error-banner">{error}</div>}
        <div ref={endRef} />
      </div>
      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
      >
        <input
          type="text"
          placeholder="Ask about your meal…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn-primary" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
