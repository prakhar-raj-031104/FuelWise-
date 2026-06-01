# FuelWise — Web App

A deployable web application built around the **FuelWise** AI mess-menu agent
(originally a Python CLI in `Week-1/submissions/mahadev/`). It wraps the agent in
a FastAPI backend, adds a React frontend (chat + menu + ratings), and runs the
LLM on self-hosted **Ollama** — packaged with Docker Compose.

```
Browser ──► Frontend (React + nginx) ──► Backend (FastAPI) ──► Ollama (llama3.2)
                                              │
                                              └─► ratings.jsonl (Docker volume)
```

## Features

- **Chat**: talk to the FuelWise agent; it calls tools (menu, nutrition, goals,
  outside food, ratings) and the UI shows a collapsible trace of which tools ran.
- **Menu**: the full weekly mess menu with today highlighted.
- **Ratings**: submit 1–5 dish ratings and view an aggregated leaderboard.

## Quick start (Docker — recommended)

From the repo root (`DevLabs2.0/`):

```bash
cp .env.example .env          # optional: tweak model / port
docker compose up --build
```

First boot pulls the model (a few minutes). Then open **http://localhost**.

Need maximum speed on weak hardware? Set `OLLAMA_MODEL=llama3.2:1b` in `.env`
(faster, but more rambling and less accurate).

### Latency

The default `llama3.2` (3B) answers in a single grounded, **streamed** pass:
the first words appear in ~1–1.5s and a complete reply lands in ~5–7s on CPU.
Tuning knobs (env vars): `OLLAMA_MODEL`, `OLLAMA_NUM_PREDICT` (answer-length
safety cap, default 300), `OLLAMA_TEMPERATURE` (default 0.3), and
`OLLAMA_KEEP_ALIVE` (keeps the model warm, default `30m`). A working GPU makes
all of this several times faster.

Ratings persist in the `ratings-data` volume across restarts:

```bash
docker compose restart backend   # ratings survive
```

## Local development (without Docker)

Requires a running Ollama (`ollama serve` + `ollama pull llama3.2`).

**Backend:**
```bash
cd app/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd app/frontend
npm install
npm run dev            # http://localhost:5173, proxies /api -> :8000
```

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | liveness + Ollama reachability + model presence |
| POST | `/api/chat` | `{message, session_id?}` → `{reply, trace, session_id}` |
| GET | `/api/menu` | full weekly menu (today flagged) |
| GET | `/api/menu/today` | today's menu |
| POST | `/api/ratings` | `{dish, rating(1-5)}` |
| GET | `/api/ratings/summary` | aggregated per-dish stats |

Interactive docs at `/docs` (e.g. http://localhost:8000/docs in dev).

## Configuration (env vars)

| Var | Default | Notes |
|-----|---------|-------|
| `OLLAMA_HOST` | `http://localhost:11434` | set to `http://ollama:11434` in compose |
| `OLLAMA_MODEL` | `llama3.2` | model to use/pull (`llama3.2:1b` for more speed) |
| `RATING_LOG` | `/tmp/mess_menu_ratings.jsonl` | JSONL ratings file (volume in prod) |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost` | comma-separated allowed origins |

## Scaling notes (next steps)

- Chat sessions are stored in an **in-memory dict** (fine for one worker). For
  multiple workers/replicas, move sessions to **Redis**.
- Menu/nutrition data and ratings are in-memory + JSONL. For a real deployment
  with editable menus and durable ratings, move to **Postgres** and add an admin
  menu editor + user accounts.
- Responses are non-streaming. Streaming (`stream: true` from Ollama, SSE to the
  browser) would improve perceived latency.
