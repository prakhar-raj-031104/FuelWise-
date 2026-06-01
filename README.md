# FuelWise

An AI mess-menu assistant for IIT Bhilai hostel students. It started as a Python
CLI agent (a DevLabs 2.0 Week 1 submission) and is now a deployable web app:
a **React** frontend, a **FastAPI** backend wrapping the agent, and a self-hosted
**Ollama** model — packaged with **Docker Compose**.

```
Browser ──► Frontend (React + nginx) ──► Backend (FastAPI) ──► Ollama (llama3.2)
                                              │
                                              └─► ratings (JSONL, persisted)
```

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

First boot pulls the model, then open **http://localhost**.

Full setup, local-dev instructions, and the API reference are in
**[app/README.md](app/README.md)**.

## Repository layout

```
app/                     # the production web application
  backend/               # FastAPI + the FuelWise agent
  frontend/              # React + Vite + TypeScript
docker-compose.yml       # Ollama + backend + frontend
.env.example             # configuration template
Week-1/                  # original DevLabs 2.0 CLI submission
```

## Tech stack

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** React, Vite, TypeScript, nginx
- **LLM:** Ollama (`llama3.2`) with tool/function calling
- **Deploy:** Docker Compose
