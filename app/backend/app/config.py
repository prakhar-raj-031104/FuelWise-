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
    # 1B is the latency-friendly default on CPU; set OLLAMA_MODEL=llama3.2 for
    # higher answer quality at the cost of speed.
    ollama_model: str = "llama3.2:1b"
    # Keep the model warm in RAM between requests (avoids ~5s cold reloads).
    ollama_keep_alive: str = "30m"
    # Cap answer length so replies stay fast and concise on CPU.
    # ~128 tokens keeps a full answer near ~5s on a CPU-only 1B model;
    # streaming means the first words still appear in well under a second.
    ollama_num_predict: int = 128

    # Ratings storage (JSONL). Backed by a Docker volume in production.
    rating_log: Path = Path("/tmp/mess_menu_ratings.jsonl")

    # CORS: comma-separated list of allowed frontend origins.
    cors_origins: str = "http://localhost:5173,http://localhost"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
