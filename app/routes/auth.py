from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request, error: str = None, msg: str = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        redirect_url = "/admin/dashboard" if user.role == "admin" else "/dashboard"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="login.html", context={"error": error, "msg": msg, "current_user": None})


@router.post("/login")
def process_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Invalid email or password", "email": email, "current_user": None},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Set session data
    request.session["user_id"] = user.id
    request.session["role"] = user.role
    request.session["user_name"] = user.name

    redirect_url = "/admin/dashboard" if user.role == "admin" else "/dashboard"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/register", response_class=HTMLResponse)
def get_register_page(request: Request, error: str = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        redirect_url = "/admin/dashboard" if user.role == "admin" else "/dashboard"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="register.html", context={"error": error, "current_user": None})


@router.post("/register")
def process_register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    clean_email = email.strip().lower()
    existing_user = db.query(User).filter(User.email == clean_email).first()
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "An account with this email already exists", "name": name, "email": email, "current_user": None},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    new_user = User(
        name=name.strip(),
        email=clean_email,
        password_hash=hash_password(password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Automatically log in after registration
    request.session["user_id"] = new_user.id
    request.session["role"] = new_user.role
    request.session["user_name"] = new_user.name

    return RedirectResponse(url="/dashboard?msg=Account created successfully!", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login?msg=You have been logged out", status_code=status.HTTP_303_SEE_OTHER)
