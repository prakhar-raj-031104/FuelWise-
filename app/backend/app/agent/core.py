"""FuelWise agent core (importable, web-friendly).

Refactored from the original CLI MessMenuAgent. Two behavioural changes versus
the CLI version:

1. run_tool no longer prints; each call is collected into a structured trace
   entry: {"tool", "args", "result"}.
2. run() accepts an existing conversation history and returns a structured
   result {"reply", "messages", "trace"} so chat can be multi-turn.

The Ollama transport (chat()) and the 6-iteration ReAct tool loop are kept as
in the original. Exceptions are unchanged so callers can map them to HTTP.
"""

import json
import re
import urllib.error
import urllib.request
from datetime import date
from typing import Any, Optional

from app.agent.data import ALL_DISHES, GOAL_GUIDES, NUTRITION_DB, OUTSIDE_OPTIONS, WEEKLY_MENU
from app.agent.errors import OllamaAPIError, OllamaModelMissing, OllamaNotRunning
from app.agent.tools import TOOL_FUNCTIONS, log_meal_rating, normalise

SYSTEM_PROMPT = (
    "You are FuelWise, a practical food-planning agent for IIT Bhilai hostel students. "
    "Today's menu, dish nutrition, and goal guidance are provided below in CONTEXT. "
    "Answer directly from that context whenever possible. "
    "Only call a tool when you genuinely need something not in the context, "
    "for example to log a meal rating or to suggest outside-campus food by budget. "
    "If no goal is provided, assume maintain. "
    "When the user mentions an allergy, check the 'allergens' field of EACH dish in the "
    "context and clearly name which items are unsafe and which are safe — never call a dish "
    "safe if its allergens list includes the stated allergen. "
    "Do not invent calorie or protein values beyond what the context lists. "
    "Reply in 2 to 3 complete sentences, then stop. Recommend specific dishes by name from "
    "today's menu. Never use bullet points, numbered lists, or nutrition tables. "
    "Always finish your final sentence — do not stop mid-thought. "
    "Be friendly and campus-realistic. Avoid medical claims."
)

MAX_TOOL_ITERATIONS = 6


def build_today_context() -> str:
    """A compact, deterministic context block so the model can answer in a single
    pass (no tool round-trip) for the common 'what should I eat' questions."""
    day = date.today().strftime("%A")
    menu = WEEKLY_MENU[day]

    lines = [f"CONTEXT — Today is {day}.", "", "Today's mess menu:"]
    lines += [f"- {meal.title()}: {', '.join(items)}" for meal, items in menu.items()]

    todays_dishes = sorted({dish for items in menu.values() for dish in items})
    lines += ["", "Nutrition for today's dishes:"]
    for dish in todays_dishes:
        info = NUTRITION_DB.get(dish)
        if info:
            allergens = ", ".join(info["allergens"]) or "none"
            lines.append(
                f"- {dish}: {info['calories']} kcal, {info['protein']}g protein, "
                f"{info['carbs']}g carbs, {info['fat']}g fat; allergens: {allergens}"
            )

    lines += ["", "Goal guidance:"]
    for goal, (summary, plate_rule, *_rest) in GOAL_GUIDES.items():
        lines.append(f"- {goal}: {summary} {plate_rule}")

    lines += ["", "Outside-campus options (when mess food is weak):"]
    for opt in OUTSIDE_OPTIONS:
        tags = " ".join(sorted(opt["tags"]))
        lines.append(f"- {opt['name']} - Rs {opt['price']} ({tags}): {opt['reason']}")

    return "\n".join(lines)


_RATING_RE = re.compile(r"([1-5])\s*(?:/\s*5|out of\s*5|stars?|star)?", re.IGNORECASE)


def _find_dish_in_text(message: str) -> Optional[str]:
    """Find a known dish mentioned anywhere in a sentence (longest match wins)."""
    norm = normalise(message)
    for dish in sorted(ALL_DISHES, key=len, reverse=True):
        if normalise(dish) in norm:
            return dish
    return None


def detect_rating(message: str) -> Optional[dict[str, Any]]:
    """Deterministic shortcut for 'log/rate <dish> as N' so rating-logging is
    instant and never depends on the model emitting a tool call."""
    text = message.lower()
    if not any(word in text for word in ("log", "rate", "rating")):
        return None
    dish = _find_dish_in_text(message)
    if not dish:
        return None
    match = _RATING_RE.search(text)
    if not match:
        return None
    rating = int(match.group(1))
    result = log_meal_rating(dish, rating)
    return {"tool": "log_meal_rating", "args": {"dish": dish, "rating": rating}, "result": result}


def parse_arguments(arguments: Any) -> dict[str, Any]:
    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


class MessMenuAgent:
    def __init__(
        self,
        model: str,
        host: str,
        keep_alive: str = "30m",
        num_predict: int = 220,
        temperature: float = 0.4,
    ) -> None:
        self.model = model
        self.host = host.rstrip("/")
        self.system_prompt = SYSTEM_PROMPT
        # Latency tuning. keep_alive keeps the model warm in RAM so we skip the
        # multi-second reload between messages; num_predict caps answer length so
        # the model can't ramble for 10s on CPU.
        self.keep_alive = keep_alive
        self.options = {"num_predict": num_predict, "temperature": temperature}

    def _payload(self, messages: list[dict[str, Any]], stream: bool) -> bytes:
        # Tools are intentionally NOT sent: all the data the model needs is
        # injected into the context (see build_today_context), so it answers in
        # a single prose pass. This avoids a second CPU generation and the
        # malformed tool-call JSON that small models (e.g. llama3.2:1b) emit.
        # Rating-logging is handled deterministically via detect_rating().
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "keep_alive": self.keep_alive,
            "options": self.options,
        }
        return json.dumps(payload).encode("utf-8")

    def _request(self, data: bytes) -> urllib.request.Request:
        return urllib.request.Request(
            f"{self.host}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

    def chat(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        request = self._request(self._payload(messages, stream=False))
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 404 or "not found" in body.lower():
                raise OllamaModelMissing from exc
            raise OllamaAPIError(f"Ollama API error {exc.code}: {body}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise OllamaNotRunning from exc

    def chat_stream(self, messages: list[dict[str, Any]]):
        """Yield Ollama's newline-delimited JSON chunks for a streaming call."""
        request = self._request(self._payload(messages, stream=True))
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                for line in response:
                    line = line.strip()
                    if line:
                        yield json.loads(line)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 404 or "not found" in body.lower():
                raise OllamaModelMissing from exc
            raise OllamaAPIError(f"Ollama API error {exc.code}: {body}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise OllamaNotRunning from exc

    def new_conversation(self) -> list[dict[str, Any]]:
        """Seed a fresh conversation with the system prompt + today's context."""
        return [{"role": "system", "content": f"{self.system_prompt}\n\n{build_today_context()}"}]

    def run(self, messages: list[dict[str, Any]], user_message: str) -> dict[str, Any]:
        """Run one user turn over an existing conversation.

        `messages` is mutated/extended in place and also returned so the caller
        can persist it for the next turn. Returns the assistant reply, the full
        updated message list, and the tool-call trace for this turn.
        """
        messages.append({"role": "user", "content": user_message})
        trace: list[dict[str, Any]] = []

        shortcut = detect_rating(user_message)
        if shortcut:
            messages.append({"role": "assistant", "content": shortcut["result"]})
            return {"reply": shortcut["result"], "messages": messages, "trace": [shortcut]}

        for _ in range(MAX_TOOL_ITERATIONS):
            message = self.chat(messages).get("message", {})
            messages.append(message)

            tool_calls = message.get("tool_calls") or []
            if not tool_calls:
                reply = message.get("content", "").strip() or "I could not generate a final recommendation."
                return {"reply": reply, "messages": messages, "trace": trace}

            for call in tool_calls:
                tool_result, entry = self.run_tool(call.get("function", {}))
                trace.append(entry)
                messages.append(tool_result)

        return {
            "reply": "I used the tools several times but could not settle on a final answer.",
            "messages": messages,
            "trace": trace,
        }

    def run_stream(self, messages: list[dict[str, Any]], user_message: str):
        """Streaming variant of run().

        Yields event dicts as work happens so the UI can render immediately:
          {"type": "tool", "tool", "args", "result"}  - a tool was called
          {"type": "token", "text": ...}              - a chunk of the answer
          {"type": "done"}                             - turn finished

        `messages` is mutated in place so the caller can persist the session.
        """
        messages.append({"role": "user", "content": user_message})

        shortcut = detect_rating(user_message)
        if shortcut:
            messages.append({"role": "assistant", "content": shortcut["result"]})
            yield {"type": "tool", **{k: shortcut[k] for k in ("tool", "args", "result")}}
            yield {"type": "token", "text": shortcut["result"]}
            yield {"type": "done"}
            return

        for _ in range(MAX_TOOL_ITERATIONS):
            content_parts: list[str] = []
            tool_calls: list[dict[str, Any]] = []

            for chunk in self.chat_stream(messages):
                msg = chunk.get("message", {})
                piece = msg.get("content")
                if piece:
                    content_parts.append(piece)
                    yield {"type": "token", "text": piece}
                if msg.get("tool_calls"):
                    tool_calls.extend(msg["tool_calls"])
                if chunk.get("done"):
                    break

            assistant_msg: dict[str, Any] = {"role": "assistant", "content": "".join(content_parts)}
            if tool_calls:
                assistant_msg["tool_calls"] = tool_calls
            messages.append(assistant_msg)

            if not tool_calls:
                yield {"type": "done"}
                return

            for call in tool_calls:
                tool_result, entry = self.run_tool(call.get("function", {}))
                yield {"type": "tool", **entry}
                messages.append(tool_result)

        yield {"type": "token", "text": "\n\n(Stopped after several tool steps without a final answer.)"}
        yield {"type": "done"}

    def run_tool(self, function_call: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
        name = function_call.get("name", "")
        arguments = parse_arguments(function_call.get("arguments", {}))

        try:
            result = TOOL_FUNCTIONS[name](**arguments)
        except KeyError:
            result = f"Unknown tool: {name}"
        except TypeError as exc:
            result = f"Tool input error for {name}: {exc}"
        except Exception as exc:  # noqa: BLE001 - surface any tool failure to the model
            result = f"Tool execution error for {name}: {exc}"

        tool_message = {"role": "tool", "tool_name": name, "content": str(result)}
        trace_entry = {"tool": name, "args": arguments, "result": str(result)}
        return tool_message, trace_entry
