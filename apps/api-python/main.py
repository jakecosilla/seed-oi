from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from api.routers import health, system, ingestion, sources
from infrastructure.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions (e.g., connect to DB)
    yield
    # Shutdown actions (e.g., disconnect from DB)

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(system.router)
    app.include_router(ingestion.router)
    app.include_router(sources.router)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
