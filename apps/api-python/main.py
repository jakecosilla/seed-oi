from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from api.routers import health, system, ingestion, sources, events, settings, overview, risks, scenarios, chat
from infrastructure.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions (e.g., connect to DB)
    yield
    # Shutdown actions (e.g., disconnect from DB)

def create_app() -> FastAPI:
    settings_conf = get_settings()
    
    app = FastAPI(
        title=settings_conf.app_name,
        version=settings_conf.app_version,
        lifespan=lifespan,
        docs_url="/docs" if settings_conf.debug else None,
        redoc_url="/redoc" if settings_conf.debug else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings_conf.cors_origins,
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
    app.include_router(overview.router)
    app.include_router(risks.router)
    app.include_router(scenarios.router)
    app.include_router(chat.router)

    return app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=settings.debug)
