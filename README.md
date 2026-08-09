# ServiceFlow – IT Service Desk Management System

A professional, beginner-friendly IT Service Desk Management System built with **Python**, **FastAPI**, **SQLAlchemy**, **SQLite**, and **Bootstrap 5**.

> **College Internship Project Note**:  
> This project was developed as a college mini-project inspired by core IT Service Management (ITSM) concepts learned during a ServiceNow virtual internship. It demonstrates enterprise ticketing workflows, role-based access control, automated state transitions, intelligent issue categorization, and performance reporting.

---

## 🌟 Key Features

1. **Role-Based Access Control (RBAC)**
   - **End User Portal**: Submit tickets, track ticket status, view personal history, search/filter tickets.
   - **Admin Workspace**: Centralized dashboard, assign tickets to IT admins, update ticket priority, manage status transitions, and export CSV reports.

2. **Intelligent Rule-Based Category Suggester**
   - Real-time keyword analysis as users type the problem description.
   - Automatically recommends appropriate category (`Hardware`, `Software`, `Network`, `Account`, `Email`) with keyword match explanations.

3. **ServiceNow-Inspired Ticket Lifecycle**
   - Enforces state machine rules: `Open` ➔ `Assigned` ➔ `In Progress` ➔ `Resolved` ➔ `Closed`.
   - Prevents invalid status jumps (e.g. jumping directly from `Open` to `Resolved` without assignment/progress).

4. **Analytics & CSV Reporting**
   - Visual dashboard breakdowns by ticket status, category, and priority.
   - One-click CSV export capability for operational auditing.

5. **Security & Session Management**
   - Password hashing using `bcrypt`.
   - Session-based authentication with strict role checks and page protection.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.13 / FastAPI
- **Database**: SQLite (`serviceflow.db`)
- **ORM**: SQLAlchemy
- **Templating**: Jinja2 (HTML5)
- **Frontend Styling**: Vanilla CSS + Bootstrap 5 (Dark Theme Header & Enterprise UI)
- **Interactive UI**: Minimal Vanilla JavaScript (AJAX for category suggestion)
- **Testing**: `pytest`, `TestClient`

---

## 📁 Project Structure

```
Internship_Proj/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application setup & route mounting
│   ├── database.py                 # SQLite database engine & session creation
│   ├── models.py                   # SQLAlchemy User & Ticket database models
│   ├── schemas.py                  # Pydantic schemas for request/response
│   ├── auth.py                     # Bcrypt hashing & session security helpers
│   ├── routes/
│   │   ├── auth.py                 # Login, Registration, Logout controllers
│   │   ├── tickets.py              # User Dashboard, Create Ticket, My Tickets, Detail
│   │   ├── admin.py                # Admin Workspace, Status Transition, Assignment
│   │   └── reports.py              # Analytics Dashboard & CSV Report Export
│   ├── services/
│   │   └── category_suggester.py   # Intelligent Keyword-based Category Suggester Engine
│   ├── static/
│   │   └── style.css               # Custom Enterprise CSS & Dark Header Styling
│   └── templates/                  # Jinja2 HTML Templates
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── create_ticket.html
│       ├── tickets.html
│       ├── ticket_detail.html
│       ├── admin_dashboard.html
│       ├── admin_tickets.html
│       └── reports.html
├── docs/
│   ├── architecture.md             # System Architecture & Component Diagram
│   ├── database.md                 # Database Schema ERD & Table Definitions
│   └── testing.md                  # Test Strategy & Pytest Guide
├── tests/
│   ├── test_auth.py
│   ├── test_tickets.py
│   ├── test_admin.py
│   └── test_category_suggester.py
├── seed.py                         # Database Seeder script
├── requirements.txt                # Python Dependencies
└── README.md                       # Project Documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed on your system.

### 2. Install Dependencies
Navigate to the project root directory and run:
```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
Run the seed script to create database tables and pre-populate sample users, admins, and tickets:
```bash
python seed.py
```

### 4. Run Development Server
Start the server using `uvicorn`:
```bash
python -m uvicorn app.main:app --reload
```

Open your browser and navigate to:  
👉 `http://127.0.0.1:8000`

---

## 🔑 Default Login Credentials

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@serviceflow.com` | `admin123` | Full access (Admin Workspace, Reports, Assignment, Status Controls) |
| **End User 1** | `john.doe@company.com` | `user123` | User Portal (Submit & Track Personal Tickets) |
| **End User 2** | `jane.smith@company.com` | `user123` | User Portal (Submit & Track Personal Tickets) |

---

## 🧪 Automated Testing

Execute the automated pytest suite (13 unit tests covering auth, tickets, isolation, admin rules, and category suggester):
```bash
pytest -v
```

---

## 🎓 College Viva Presentation Guide

### Q1: What ServiceNow / ITSM concepts are implemented in this project?
**Answer**: ServiceFlow implements core IT Service Management (ITSM) principles, including:
1. **Incident/Service Request Management**: Structured intake, categorization, and tracking of IT issues.
2. **Role Separation**: Distinction between End Users (requestors) and IT Support Admins (fulfillers).
3. **Ticket Lifecycle State Machine**: Controlled status progression (`Open` ➔ `Assigned` ➔ `In Progress` ➔ `Resolved` ➔ `Closed`).
4. **SLA & Priority Escalation**: Categorizing impact from `Low` to `Critical`.

### Q2: How does the Intelligent Category Suggestion feature work?
**Answer**: It uses a lightweight, rule-based natural language processing algorithm located in `app/services/category_suggester.py`. As the user types in the ticket description, JavaScript calls `/api/suggest-category`. The backend scans text for regex keyword patterns (e.g., "wifi", "router", "vpn" ➔ Network; "laptop", "monitor", "keyboard" ➔ Hardware). It returns a suggested category and confidence level.

### Q3: How is security handled for passwords and sessions?
**Answer**: Passwords are never stored in plain text; they are hashed using `bcrypt` (a salted hashing algorithm). Sessions are managed using Starlette `SessionMiddleware` signed cookies, and backend dependencies (`require_user`, `require_admin`) enforce access control on every endpoint.

### Q4: Why FastAPI and SQLAlchemy instead of Flask or Django?
**Answer**: 
- **FastAPI**: Modern, fast Python framework with built-in asynchronous support, automatic validation via Pydantic, and clear routing structure.
- **SQLAlchemy**: Enterprise-grade Object-Relational Mapper (ORM) that abstracts database SQL queries into Python objects, preventing SQL injection vulnerabilities.
