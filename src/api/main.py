"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.models import HealthResponse
from src.api.routes import generate, posts, queue, settings, trending, chat, auth, scheduler as scheduler_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    from src.scheduler import PostingScheduler
    from src.db.settings import SettingsDB

    settings_db = SettingsDB()
    config = settings_db.get_scheduler_config()

    if config.get("enabled", True):
        app.state.scheduler = PostingScheduler()
        await app.state.scheduler.start()

    yield

    if hasattr(app.state, "scheduler"):
        app.state.scheduler.stop()


app = FastAPI(
    title="x-generator",
    description="Stoic-themed X/Twitter content generator with web dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router)
app.include_router(posts.router)
app.include_router(queue.router)
app.include_router(settings.router)
app.include_router(trending.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(scheduler_routes.router)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
