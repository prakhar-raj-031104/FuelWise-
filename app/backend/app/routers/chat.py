"""Chat endpoint wrapping the FuelWise agent.

Declared as a sync `def` so FastAPI runs the blocking Ollama call in its
threadpool instead of blocking the event loop. Conversation state lives in an
in-memory dict keyed by session id (single-worker MVP; swap for Redis to scale).
"""

import json
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agent.core import MessMenuAgent
from app.agent.errors import OllamaAPIError, OllamaModelMissing, OllamaNotRunning
from app.config import settings
from app.schemas import ChatRequest, ChatResponse

router = APIRouter()

agent = MessMenuAgent(
    model=settings.ollama_model,
    host=settings.ollama_host,
    keep_alive=settings.ollama_keep_alive,
    num_predict=settings.ollama_num_predict,
    temperature=settings.ollama_temperature,
)

# session_id -> message history (includes the system prompt at index 0).
_sessions: dict[str, list[dict[str, Any]]] = {}


def _resolve_session(session_id: str | None) -> tuple[str, list[dict[str, Any]]]:
    if not session_id or session_id not in _sessions:
        session_id = session_id or uuid.uuid4().hex
        _sessions[session_id] = agent.new_conversation()
    return session_id, _sessions[session_id]


@router.post("/chat/stream")
def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Stream the agent's reply as Server-Sent Events.

    Emits `data: {json}` lines where json is one of:
      {"type": "session", "session_id": ...}  (first, so the client can persist it)
      {"type": "tool", "tool", "args", "result"}
      {"type": "token", "text": ...}
      {"type": "done"}
      {"type": "error", "detail": ...}
    """
    session_id, messages = _resolve_session(request.session_id)

    def sse(event: dict) -> str:
        return f"data: {json.dumps(event)}\n\n"

    def event_stream():
        yield sse({"type": "session", "session_id": session_id})
        try:
            for event in agent.run_stream(messages, request.message):
                yield sse(event)
        except OllamaNotRunning:
            yield sse({
                "type": "error",
                "detail": "FuelWise's local model (Ollama) is not running. Start it with: ollama serve",
            })
        except OllamaModelMissing:
            yield sse({
                "type": "error",
                "detail": f"Ollama is up but the model '{settings.ollama_model}' is not pulled. "
                f"Run: ollama pull {settings.ollama_model}",
            })
        except OllamaAPIError as exc:
            yield sse({"type": "error", "detail": f"Ollama API error: {exc}"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    session_id, messages = _resolve_session(request.session_id)

    try:
        result = agent.run(messages, request.message)
    except OllamaNotRunning as exc:
        raise HTTPException(
            status_code=503,
            detail="FuelWise's local model (Ollama) is not running. Start it with 'ollama serve'.",
        ) from exc
    except OllamaModelMissing as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama is up but the model '{settings.ollama_model}' is not pulled. "
            f"Run: ollama pull {settings.ollama_model}",
        ) from exc
    except OllamaAPIError as exc:
        raise HTTPException(status_code=502, detail=f"Ollama API error: {exc}") from exc

    _sessions[session_id] = result["messages"]
    return ChatResponse(reply=result["reply"], trace=result["trace"], session_id=session_id)
