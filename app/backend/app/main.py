"""FuelWise FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, health, menu, ratings

app = FastAPI(
    title="FuelWise API",
    description="AI mess-menu assistant for IIT Bhilai hostel students.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(menu.router, prefix="/api", tags=["menu"])
app.include_router(ratings.router, prefix="/api", tags=["ratings"])


@app.get("/")
def root() -> dict:
    return {"name": "FuelWise API", "docs": "/docs", "health": "/api/health"}
