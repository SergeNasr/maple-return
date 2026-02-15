"""FastAPI application for Maple Return property investment analyzer."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine
from .db_models import PropertyConfig  # noqa: F401 - imported for Base.metadata
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events.

    Creates database tables on startup and handles cleanup on shutdown.
    This replaces the deprecated on_event decorator.
    """
    # Startup: create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: cleanup would go here if needed


# Create FastAPI application with lifespan handler
app = FastAPI(title="Maple Return", lifespan=lifespan)

# Configure Jinja2 templates
templates = Jinja2Templates(directory="maple_return/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="maple_return/static"), name="static")

# Include API router
app.include_router(router)


@app.get("/")
async def index(request: Request):
    """Home page route - test page to verify web server is working.

    Returns:
        TemplateResponse: Rendered index.html template with test content
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Maple Return - Test Page",
            "message": "Foundation phase: Web server is running successfully",
        },
    )
