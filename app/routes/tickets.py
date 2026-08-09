import os
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, Ticket
from app.auth import get_current_user, require_user
from app.services.category_suggester import suggest_category

router = APIRouter(tags=["tickets"])

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/", response_class=HTMLResponse)
def index_redirect(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    if user.role == "admin":
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)


@router.get("/dashboard", response_class=HTMLResponse)
def user_dashboard(request: Request, msg: str = None, error: str = None, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if user.role == "admin":
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

    # Fetch counts for logged in user
    user_tickets = db.query(Ticket).filter(Ticket.user_id == user.id)
    total_tickets = user_tickets.count()
    open_tickets = user_tickets.filter(Ticket.status == "Open").count()
    in_progress_tickets = user_tickets.filter(Ticket.status == "In Progress").count()
    assigned_tickets = user_tickets.filter(Ticket.status == "Assigned").count()
    resolved_closed_tickets = user_tickets.filter(Ticket.status.in_(["Resolved", "Closed"])).count()

    recent_tickets = user_tickets.order_by(Ticket.created_at.desc()).limit(5).all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "current_user": user,
            "msg": msg,
            "error": error,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "assigned_tickets": assigned_tickets,
            "in_progress_tickets": in_progress_tickets,
            "resolved_closed_tickets": resolved_closed_tickets,
            "recent_tickets": recent_tickets
        }
    )


@router.get("/tickets", response_class=HTMLResponse)
def my_tickets(
    request: Request,
    search: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    user = require_user(request, db)

    query = db.query(Ticket).filter(Ticket.user_id == user.id)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Ticket.title.ilike(search_term),
                Ticket.description.ilike(search_term)
            )
        )

    if category:
        query = query.filter(Ticket.category == category)

    if status_filter:
        query = query.filter(Ticket.status == status_filter)

    tickets_list = query.order_by(Ticket.created_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="tickets.html",
        context={
            "current_user": user,
            "tickets": tickets_list,
            "search": search or "",
            "category": category or "",
            "status_filter": status_filter or ""
        }
    )


@router.get("/tickets/create", response_class=HTMLResponse)
def create_ticket_form(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    return templates.TemplateResponse(request=request, name="create_ticket.html", context={"current_user": user})


@router.post("/tickets/create")
def process_create_ticket(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    priority: str = Form("Medium"),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)

    valid_categories = ["Hardware", "Software", "Network", "Account", "Email", "Other"]
    valid_priorities = ["Low", "Medium", "High", "Critical"]

    if category not in valid_categories:
        category = "Other"

    if priority not in valid_priorities:
        priority = "Medium"

    new_ticket = Ticket(
        title=title.strip(),
        description=description.strip(),
        category=category,
        priority=priority,
        status="Open",
        user_id=user.id
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return RedirectResponse(
        url=f"/tickets/{new_ticket.id}?msg=Ticket #{new_ticket.id} created successfully!",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/tickets/{ticket_id}", response_class=HTMLResponse)
def view_ticket_detail(request: Request, ticket_id: int, msg: str = None, error: str = None, db: Session = Depends(get_db)):
    user = require_user(request, db)

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Access control: standard users can only view their own tickets
    if user.role != "admin" and ticket.user_id != user.id:
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "current_user": user,
                "error": "Access Denied: You can only view your own tickets.",
                "total_tickets": 0, "open_tickets": 0, "assigned_tickets": 0,
                "in_progress_tickets": 0, "resolved_closed_tickets": 0, "recent_tickets": []
            },
            status_code=status.HTTP_403_FORBIDDEN
        )

    return templates.TemplateResponse(
        request=request,
        name="ticket_detail.html",
        context={
            "current_user": user,
            "ticket": ticket,
            "msg": msg,
            "error": error
        }
    )


@router.post("/api/suggest-category")
async def api_suggest_category(request: Request):
    """API endpoint for intelligent keyword-based category suggestion."""
    try:
        data = await request.json()
        description = data.get("description", "")
        suggestion = suggest_category(description)
        return JSONResponse(content=suggestion)
    except Exception as e:
        return JSONResponse(
            content={"suggested_category": "Other", "confidence": "None", "matched_keywords": []},
            status_code=status.HTTP_400_BAD_REQUEST
        )
