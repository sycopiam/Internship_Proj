import os
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, Ticket
from app.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Valid state machine transitions
ALLOWED_STATUS_TRANSITIONS = {
    "Open": ["Assigned", "Closed"],
    "Assigned": ["In Progress", "Open", "Closed"],
    "In Progress": ["Resolved", "Assigned", "Closed"],
    "Resolved": ["Closed", "In Progress"],
    "Closed": ["Open"]  # Admin can reopen closed ticket
}


@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, msg: str = None, error: str = None, db: Session = Depends(get_db)):
    admin_user = require_admin(request, db)

    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == "Open").count()
    assigned_tickets = db.query(Ticket).filter(Ticket.status == "Assigned").count()
    in_progress_tickets = db.query(Ticket).filter(Ticket.status == "In Progress").count()
    resolved_tickets = db.query(Ticket).filter(Ticket.status == "Resolved").count()
    closed_tickets = db.query(Ticket).filter(Ticket.status == "Closed").count()
    high_critical_tickets = db.query(Ticket).filter(Ticket.priority.in_(["High", "Critical"])).count()

    recent_tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).limit(8).all()

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "current_user": admin_user,
            "msg": msg,
            "error": error,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "assigned_tickets": assigned_tickets,
            "in_progress_tickets": in_progress_tickets,
            "resolved_tickets": resolved_tickets,
            "closed_tickets": closed_tickets,
            "high_critical_tickets": high_critical_tickets,
            "recent_tickets": recent_tickets
        }
    )


@router.get("/tickets", response_class=HTMLResponse)
def admin_tickets(
    request: Request,
    search: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status_filter: Optional[str] = None,
    msg: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    admin_user = require_admin(request, db)

    query = db.query(Ticket).join(User, Ticket.user_id == User.id)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Ticket.title.ilike(search_term),
                Ticket.description.ilike(search_term),
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    if category:
        query = query.filter(Ticket.category == category)

    if priority:
        query = query.filter(Ticket.priority == priority)

    if status_filter:
        query = query.filter(Ticket.status == status_filter)

    tickets_list = query.order_by(Ticket.created_at.desc()).all()
    admins_list = db.query(User).filter(User.role == "admin").all()

    return templates.TemplateResponse(
        request=request,
        name="admin_tickets.html",
        context={
            "current_user": admin_user,
            "tickets": tickets_list,
            "admins": admins_list,
            "search": search or "",
            "category": category or "",
            "priority": priority or "",
            "status_filter": status_filter or "",
            "msg": msg,
            "error": error
        }
    )


@router.post("/tickets/{ticket_id}/status")
def update_ticket_status(
    request: Request,
    ticket_id: int,
    new_status: str = Form(...),
    db: Session = Depends(get_db)
):
    admin_user = require_admin(request, db)
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    current_st = ticket.status
    allowed_next = ALLOWED_STATUS_TRANSITIONS.get(current_st, [])

    if new_status != current_st and new_status not in allowed_next:
        err_msg = f"Invalid status transition: Cannot change status from '{current_st}' directly to '{new_status}'."
        return RedirectResponse(
            url=f"/tickets/{ticket_id}?error={err_msg}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    ticket.status = new_status
    ticket.updated_at = datetime.now(timezone.utc)
    db.commit()

    return RedirectResponse(
        url=f"/tickets/{ticket_id}?msg=Ticket #{ticket.id} status updated to '{new_status}' successfully!",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/tickets/{ticket_id}/priority")
def update_ticket_priority(
    request: Request,
    ticket_id: int,
    new_priority: str = Form(...),
    db: Session = Depends(get_db)
):
    admin_user = require_admin(request, db)
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    valid_priorities = ["Low", "Medium", "High", "Critical"]
    if new_priority in valid_priorities:
        ticket.priority = new_priority
        ticket.updated_at = datetime.now(timezone.utc)
        db.commit()

    return RedirectResponse(
        url=f"/tickets/{ticket_id}?msg=Ticket #{ticket.id} priority updated to '{new_priority}'!",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/tickets/{ticket_id}/assign")
def assign_ticket(
    request: Request,
    ticket_id: int,
    assignee_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    admin_user = require_admin(request, db)
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if assignee_id:
        target_admin = db.query(User).filter(User.id == assignee_id, User.role == "admin").first()
        if target_admin:
            ticket.assigned_to = target_admin.id
            if ticket.status == "Open":
                ticket.status = "Assigned"
            ticket.updated_at = datetime.now(timezone.utc)
            db.commit()
    else:
        ticket.assigned_to = None
        ticket.updated_at = datetime.now(timezone.utc)
        db.commit()

    return RedirectResponse(
        url=f"/tickets/{ticket_id}?msg=Ticket assignment updated!",
        status_code=status.HTTP_303_SEE_OTHER
    )
