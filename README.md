<div align="center">

# 🍽️ FuelWise

**An AI mess-menu assistant for hostel students — chat your way to a better plate.**

Ask what to eat, get instant, goal-aware advice grounded in the real weekly menu,
nutrition data, and your budget — powered by a self-hosted LLM, no API keys required.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Ollama](https://img.shields.io/badge/Ollama-llama3.2-000000?logo=ollama&logoColor=white)](https://ollama.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#-license)

</div>

---

## Overview

FuelWise started as a command-line AI agent (a DevLabs 2.0 Week 1 submission) and is now a
full, deployable web application. It helps hostel students answer the daily question —
*"what should I eat?"* — by combining a chat assistant with the real mess menu, dish
nutrition, fitness-goal guidance, budget-aware outside-food suggestions, and a community
ratings leaderboard.

The language model runs **locally via [Ollama](https://ollama.com/)**, so the app is free to
run, private by default, and requires **no paid API keys**.

## Features

- 💬 **Conversational assistant** — ask about meals, fitness goals (bulk/cut/maintain),
  allergies, cravings, and budgets; replies **stream token-by-token** for an instant feel.
- 📅 **Weekly menu** — the full mess menu with today highlighted.
- ⭐ **Ratings leaderboard** — rate dishes 1–5 and see aggregated community favourites.
- 🥗 **Grounded answers** — recommendations are based on the actual menu and a curated
  nutrition database, not model guesswork.
- ⚡ **Fast on CPU** — context-grounded single-pass generation + response streaming keep
  replies responsive even without a GPU.
- 🐳 **One-command deploy** — `docker compose up` brings up the model, API, and UI together.

## Architecture

```
┌────────────┐     HTTP      ┌──────────────┐   /api/chat/stream (SSE)   ┌───────────────┐
│  Browser   │ ───────────▶  │   Frontend   │ ─────────────────────────▶ │    Backend    │
│  (React)   │ ◀───────────  │ React+nginx  │ ◀───────────────────────── │   (FastAPI)   │
└────────────┘   SSE stream  └──────────────┘                            └───────┬───────┘
                                                                                 │
                                            ┌────────────────────────────────────┼───────────────┐
                                            ▼                                     ▼               ▼
                                   ┌──────────────┐                     ┌──────────────┐  ┌──────────────┐
                                   │    Ollama    │                     │ Menu/Nutri/  │  │ Ratings      │
                                   │ (llama3.2)   │                     │ Goal context │  │ (JSONL store)│
                                   └──────────────┘                     └──────────────┘  └──────────────┘
```

**How the assistant works:** instead of multi-step tool-calling (slow on CPU and unreliable on
small models), the backend deterministically assembles a compact context block — today's menu,
nutrition for those dishes, goal guidance, and outside-food options — and asks the model to
answer in a single streamed pass. Rating commands (e.g. *"Log Paneer Curry as 4/5"*) are
detected and executed without an LLM call, so they're instant.

## Tech Stack

| Layer        | Technology                                              |
| ------------ | ------------------------------------------------------- |
| Frontend     | React 18, TypeScript, Vite, `react-markdown`, nginx     |
| Backend      | Python 3.12, FastAPI, Uvicorn, pydantic-settings        |
| LLM runtime  | Ollama (`llama3.2` by default; `llama3.2:1b` for speed) |
| Streaming    | Server-Sent Events (SSE)                                |
| Persistence  | JSONL ratings log (Docker volume)                       |
| Packaging    | Docker, Docker Compose                                   |

## Getting Started

### Option 1 — Docker (recommended)

> Requires [Docker](https://docs.docker.com/get-docker/) and Docker Compose.

```bash
git clone https://github.com/<your-username>/fuelwise.git
cd fuelwise
cp .env.example .env          # optional: tweak model / port
docker compose up --build
```

The first boot pulls the model (a few minutes / a couple of GB). When ready, open
**http://localhost**.

### Option 2 — Local development

> Requires Python 3.12+, Node.js 20+, and a running [Ollama](https://ollama.com/).

**1. Start Ollama and pull the model**
```bash
ollama serve
ollama pull llama3.2
```

**2. Backend**
```bash
cd app/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**3. Frontend**
```bash
cd app/frontend
npm install
npm run dev        # http://localhost:5173 (proxies /api → :8000)
```

> If port 8000 is taken, run the backend on another port and point the dev server at it:
> `VITE_API_TARGET=http://localhost:8010 npm run dev`.

## Configuration

All settings are environment variables (see [`.env.example`](.env.example)):

| Variable             | Default                          | Description                                                        |
| -------------------- | -------------------------------- | ------------------------------------------------------------------ |
| `OLLAMA_MODEL`       | `llama3.2`                       | Model to use/pull. Set `llama3.2:1b` for more speed on weak hardware. |
| `OLLAMA_HOST`        | `http://localhost:11434`         | Ollama endpoint (`http://ollama:11434` inside Compose).            |
| `OLLAMA_KEEP_ALIVE`  | `30m`                            | Keeps the model warm in RAM to avoid cold-load latency.            |
| `OLLAMA_NUM_PREDICT` | `300`                            | Max answer length (safety cap; answers finish naturally below it). |
| `OLLAMA_TEMPERATURE` | `0.3`                            | Sampling temperature — lower = more factual/deterministic.         |
| `RATING_LOG`         | `/tmp/mess_menu_ratings.jsonl`   | Ratings file path (a Docker volume in production).                 |
| `CORS_ORIGINS`       | `http://localhost:5173,http://localhost` | Comma-separated allowed frontend origins.                  |
| `FRONTEND_PORT`      | `80`                             | Host port the web app is served on (Compose).                      |

## API Reference

Interactive docs are available at `/docs` (Swagger UI) when the backend is running.

| Method | Endpoint               | Description                                                  |
| ------ | ---------------------- | ------------------------------------------------------------ |
| `GET`  | `/api/health`          | Liveness + Ollama reachability + whether the model is pulled |
| `POST` | `/api/chat`            | Non-streaming chat: `{message, session_id?}` → `{reply, trace, session_id}` |
| `POST` | `/api/chat/stream`     | Streaming chat (SSE): emits `session`, `tool`, `token`, `done` events |
| `GET`  | `/api/menu`            | Full weekly menu (today flagged)                             |
| `GET`  | `/api/menu/today`      | Today's menu                                                 |
| `POST` | `/api/ratings`         | Submit a rating: `{dish, rating (1–5)}`                      |
| `GET`  | `/api/ratings/summary` | Aggregated per-dish stats for the leaderboard                |

## Project Structure

```
fuelwise/
├── app/
│   ├── backend/                 # FastAPI service
│   │   ├── app/
│   │   │   ├── agent/           # the FuelWise agent: data, tools, core, context
│   │   │   ├── routers/         # chat, menu, ratings, health endpoints
│   │   │   ├── services/        # ratings JSONL store
│   │   │   ├── config.py        # env-driven settings
│   │   │   └── main.py          # app entrypoint
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── frontend/                # React + Vite + TS SPA
│   │   ├── src/
│   │   │   ├── api/             # typed API client (incl. SSE streaming)
│   │   │   └── components/      # ChatWindow, MenuView, RatingsDashboard, …
│   │   ├── nginx.conf
│   │   └── Dockerfile
│   └── README.md                # app-level developer notes
├── Week-1/                      # original DevLabs 2.0 CLI submission
├── docker-compose.yml           # Ollama + backend + frontend
├── .env.example
└── README.md
```

## Performance Notes

On CPU-only machines, FuelWise is tuned to feel responsive:
- A **warm-kept model** (`keep_alive=30m`) avoids cold reloads between messages.
- **Context grounding** lets the model answer in a single pass (no slow tool round-trips).
- **Streaming** surfaces the first words in well under a second.
- A **bounded answer length** keeps full replies near ~5 seconds.

A working GPU makes everything several times faster; switch to `OLLAMA_MODEL=llama3.2` for
richer answers in that case.

## Roadmap

- [ ] User accounts with saved profiles (goal, allergies)
- [ ] Admin UI to edit the weekly menu
- [ ] Redis-backed sessions for horizontal scaling
- [ ] Postgres-backed menu and ratings
- [ ] Push daily recommendations via WhatsApp/Telegram

## Contributing

Contributions are welcome. Please open an issue to discuss substantial changes first, then:

1. Fork the repository and create a feature branch.
2. Make your changes (keep the backend importable and the frontend type-clean: `npm run build`).
3. Open a pull request with a clear description.

## License

Released under the [MIT License](#-license). Add a `LICENSE` file with your name as the
copyright holder before publishing.

## Acknowledgements

- Built with [Ollama](https://ollama.com/), [FastAPI](https://fastapi.tiangolo.com/), and [React](https://react.dev/).
- Originally created as a **DevLabs 2.0** Week 1 AI-agent submission.
