from typing import Optional
import bcrypt
from fastapi import Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed bcrypt password."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Retrieves current user from session if logged in."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    return user


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Dependency that enforces user login. Redirects HTML requests to login page."""
    user = get_current_user(request, db)
    if not user:
        # Check if JSON request or browser page navigation
        if "application/json" in request.headers.get("accept", ""):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/auth/login?error=Please log in to continue"}
        )
    return user


def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    """Dependency that enforces admin role. Redirects or raises 403."""
    user = require_user(request, db)
    if user.role != "admin":
        if "application/json" in request.headers.get("accept", ""):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/dashboard?error=Admin access required"}
        )
    return user
