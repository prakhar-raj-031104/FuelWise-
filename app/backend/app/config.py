"""Application settings loaded from environment variables.

Uses pydantic-settings so every value is overridable via env (and thus via
docker-compose). Defaults match the original CLI so local dev works unchanged.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Ollama
    ollama_host: str = "http://localhost:11434"
    # 3B (llama3.2) gives more accurate, instruction-following answers; with a
    # single streamed generation it lands around ~5-7s on CPU (first token < ~1.5s).
    # For maximum speed on weak hardware, set OLLAMA_MODEL=llama3.2:1b.
    ollama_model: str = "llama3.2"
    # Keep the model warm in RAM between requests (avoids cold reloads).
    ollama_keep_alive: str = "30m"
    # Lower temperature = more factual, deterministic answers (e.g. allergy checks).
    ollama_temperature: float = 0.3
    # Safety cap on answer length. Set generously so the model finishes its
    # answer naturally (a complete sentence) rather than being cut off mid-word;
    # the brevity instruction in the system prompt keeps answers short, so this
    # cap is rarely the limiter. Streaming shows the first words in under a second.
    ollama_num_predict: int = 300

    # Ratings storage (JSONL). Backed by a Docker volume in production.
    rating_log: Path = Path("/tmp/mess_menu_ratings.jsonl")

    # CORS: comma-separated list of allowed frontend origins.
    cors_origins: str = "http://localhost:5173,http://localhost"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
