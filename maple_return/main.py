"""FastAPI application for Maple Return property investment analyzer."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine

# Create FastAPI application
app = FastAPI(title="Maple Return")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="maple_return/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="maple_return/static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup.

    Creates all tables defined in SQLAlchemy models when the server starts.
    This ensures the database schema is ready before handling requests.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def index(request: Request):
    """Home page route - test page to verify web server is working.

    Returns:
        TemplateResponse: Rendered index.html template with test content
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Maple Return - Test Page",
            "message": "Foundation phase: Web server is running successfully",
        },
    )
