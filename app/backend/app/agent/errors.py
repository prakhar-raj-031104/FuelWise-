"""Ollama-related error types, preserved from the original CLI."""


class OllamaNotRunning(RuntimeError):
    """Ollama is unreachable (server not started / wrong host)."""


class OllamaModelMissing(RuntimeError):
    """Ollama is up but the requested model has not been pulled."""


class OllamaAPIError(RuntimeError):
    """Ollama returned an unexpected HTTP error."""
