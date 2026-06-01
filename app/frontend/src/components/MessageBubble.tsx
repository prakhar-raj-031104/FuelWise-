import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { TraceEntry } from "../api/client";
import { ToolTrace } from "./ToolTrace";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  trace?: TraceEntry[];
}

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`bubble-row ${isUser ? "user" : "assistant"}`}>
      <div className={`avatar ${isUser ? "me" : "bot"}`}>{isUser ? "🧑" : "🍽️"}</div>
      <div className={`bubble ${isUser ? "user" : "assistant"}`}>
        {isUser ? (
          <div>{message.content}</div>
        ) : message.content ? (
          <div className="md">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>
        ) : (
          <span className="dots">
            <span></span>
            <span></span>
            <span></span>
          </span>
        )}
        {!isUser && message.trace && <ToolTrace trace={message.trace} />}
      </div>
    </div>
  );
}
