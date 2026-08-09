import csv
import io
import os
from datetime import datetime
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Ticket
from app.auth import require_admin

router = APIRouter(prefix="/admin/reports", tags=["reports"])

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def reports_dashboard(request: Request, db: Session = Depends(get_db)):
    admin_user = require_admin(request, db)

    # Breakdown by Status
    status_counts = dict(
        db.query(Ticket.status, func.count(Ticket.id))
        .group_by(Ticket.status)
        .all()
    )
    all_statuses = ["Open", "Assigned", "In Progress", "Resolved", "Closed"]
    status_data = {s: status_counts.get(s, 0) for s in all_statuses}

    # Breakdown by Category
    category_counts = dict(
        db.query(Ticket.category, func.count(Ticket.id))
        .group_by(Ticket.category)
        .all()
    )
    all_categories = ["Hardware", "Software", "Network", "Account", "Email", "Other"]
    category_data = {c: category_counts.get(c, 0) for c in all_categories}

    # Breakdown by Priority
    priority_counts = dict(
        db.query(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
        .all()
    )
    all_priorities = ["Low", "Medium", "High", "Critical"]
    priority_data = {p: priority_counts.get(p, 0) for p in all_priorities}

    total_tickets = db.query(Ticket).count()

    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "current_user": admin_user,
            "total_tickets": total_tickets,
            "status_data": status_data,
            "category_data": category_data,
            "priority_data": priority_data
        }
    )


@router.get("/export-csv")
def export_csv_report(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)

    tickets = db.query(Ticket).order_by(Ticket.id.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV Header
    writer.writerow([
        "Ticket ID",
        "Title",
        "Category",
        "Priority",
        "Status",
        "Created By",
        "User Email",
        "Assigned Admin",
        "Created Date",
        "Updated Date"
    ])

    for t in tickets:
        creator_name = t.creator.name if t.creator else "Unknown"
        creator_email = t.creator.email if t.creator else ""
        assignee_name = t.assignee.name if t.assignee else "Unassigned"
        created_str = t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else ""
        updated_str = t.updated_at.strftime("%Y-%m-%d %H:%M:%S") if t.updated_at else ""

        writer.writerow([
            t.id,
            t.title,
            t.category,
            t.priority,
            t.status,
            creator_name,
            creator_email,
            assignee_name,
            created_str,
            updated_str
        ])

    csv_filename = f"ServiceFlow_Ticket_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={csv_filename}"
        }
    )
