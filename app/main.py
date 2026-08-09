import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.database import engine, Base
from app.routes import auth, tickets, admin, reports

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ServiceFlow – IT Service Desk Management System",
    description="ServiceDesk ITSM management web app inspired by ServiceNow concepts",
    version="1.0.0"
)

# Secret key for session management
SECRET_KEY = os.getenv("SECRET_KEY", "serviceflow-secret-key-college-proj-2026")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Static and Templates directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Register Routers
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(admin.router)
app.include_router(reports.router)

templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={
            "current_user": None,
            "error": "Page not found (404)"
        },
        status_code=404
    )
