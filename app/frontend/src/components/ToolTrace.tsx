import { useState } from "react";
import type { TraceEntry } from "../api/client";

// Collapsible panel showing which tools the agent called for a reply.
// Mirrors the CLI's "-> Calling ... <- Result ..." trace, but in the UI.
export function ToolTrace({ trace }: { trace: TraceEntry[] }) {
  const [open, setOpen] = useState(false);
  if (trace.length === 0) return null;

  return (
    <div className="tool-trace">
      <button className="tool-trace-toggle" onClick={() => setOpen((v) => !v)}>
        {open ? "▾" : "▸"} Agent used {trace.length} tool{trace.length > 1 ? "s" : ""}
      </button>
      {open && (
        <ul className="tool-trace-list">
          {trace.map((entry, i) => (
            <li key={i}>
              <code className="tool-name">
                {entry.tool}({Object.entries(entry.args).map(([k, v]) => `${k}=${JSON.stringify(v)}`).join(", ")})
              </code>
              <div className="tool-result">{entry.result}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
