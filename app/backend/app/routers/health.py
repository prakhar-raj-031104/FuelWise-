"""Health endpoint: liveness plus Ollama reachability and model presence."""

import json
import urllib.error
import urllib.request

from fastapi import APIRouter

from app.config import settings
from app.schemas import HealthResponse

router = APIRouter()


def _ollama_status() -> tuple[bool, bool]:
    """Return (reachable, model_present) by querying Ollama's /api/tags."""
    url = f"{settings.ollama_host.rstrip('/')}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return False, False

    names = {model.get("name", "") for model in data.get("models", [])}
    # Ollama tags look like "llama3.2:latest"; match on the base name too.
    wanted = settings.ollama_model
    present = any(name == wanted or name.split(":")[0] == wanted.split(":")[0] for name in names)
    return True, present


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    reachable, model_present = _ollama_status()
    return HealthResponse(
        status="ok",
        ollama_reachable=reachable,
        model_present=model_present,
        model=settings.ollama_model,
    )
