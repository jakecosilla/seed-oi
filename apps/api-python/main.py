from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from api.routers import health, system, ingestion, sources, events, settings
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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(system.router)
    app.include_router(ingestion.router)
    app.include_router(sources.router)
    app.include_router(events.router)
    app.include_router(settings.router)

    return app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=settings.debug)
