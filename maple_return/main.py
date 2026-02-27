"""FastAPI application for Maple Return property investment analyzer."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine, get_db
from .db_models import PropertyConfig  # noqa: F401 - imported for Base.metadata
from .routes import router, simulate


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


def _numerify(obj):
    """Recursively convert string-encoded numbers back to floats for template rendering."""
    if isinstance(obj, dict):
        return {k: _numerify(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_numerify(item) for item in obj]
    if isinstance(obj, str):
        try:
            return float(obj)
        except ValueError:
            return obj
    return obj


@app.get("/")
async def index(request: Request):
    """Home page route - shows results if valid data exists, otherwise redirects to wizard.

    Runs the simulation using saved config and renders results page.
    If no config exists or config is incomplete, redirects to wizard.

    Returns:
        TemplateResponse: Rendered results.html with simulation data
        RedirectResponse: Redirects to /wizard if config missing/incomplete
    """
    async for db in get_db():
        try:
            simulation_data = await simulate(db)
        except Exception:
            return RedirectResponse(url="/wizard")

        simulation_data = _numerify(simulation_data)
        simulation_data["request"] = request
        return templates.TemplateResponse(name="results.html", context=simulation_data)

    return RedirectResponse(url="/wizard")


@app.get("/wizard")
async def wizard(request: Request):
    """Property wizard page - multi-step form for property data entry.

    Returns:
        TemplateResponse: Rendered wizard.html template
    """
    return templates.TemplateResponse(request=request, name="wizard.html")
