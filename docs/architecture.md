# ServiceFlow - System Architecture & Design

## Overview
ServiceFlow is an IT Service Desk Management System built with Python, FastAPI, SQLAlchemy, and Bootstrap 5. It implements key IT Service Management (ITSM) principles inspired by enterprise platforms like ServiceNow.

```
+-----------------------------------------------------------------------+
|                             USER BROWSER                               |
|            Bootstrap 5 UI / HTML5 Templates / Dynamic JS               |
+-----------------------------------+-----------------------------------+
                                    | HTTP Requests (Form / API)
                                    v
+-----------------------------------------------------------------------+
|                           FASTAPI APPLICATION                          |
|                                                                       |
|  +-------------------+  +-------------------+  +-------------------+  |
|  |    Auth Router    |  |  Tickets Router   |  |   Admin Router    |  |
|  |  (Login/Register) |  |  (User Dashboard) |  | (Manage/Reports)  |  |
|  +---------+---------+  +---------+---------+  +---------+---------+  |
|            |                      |                      |            |
|            v                      v                      v            |
|  +-----------------------------------------------------------------+  |
|  |                  Session & Role Guard Layer                     |  |
|  +-----------------------------------------------------------------+  |
|                                   |                                   |
|                                   v                                   |
|  +-----------------------------------------------------------------+  |
|  |             Rule Engine: Category Suggester Module               |  |
|  +-----------------------------------------------------------------+  |
|                                   |                                   |
+-----------------------------------+-----------------------------------+
                                    | SQLAlchemy ORM
                                    v
+-----------------------------------------------------------------------+
|                          SQLITE DATABASE                              |
|                   Tables: users, tickets                              |
+-----------------------------------------------------------------------+
```

## Key Components

1. **Authentication & Session Security (`app/auth.py`, `app/routes/auth.py`)**:
   - Manages user login and registration.
   - Enforces password security using `bcrypt` salted hashes.
   - Enforces role-based session middleware (User vs. Admin).

2. **User Ticket Management (`app/routes/tickets.py`)**:
   - Ticket submission with real-time intelligent category recommendation.
   - User ticket dashboard with live status cards and isolation guards.

3. **Intelligent Category Engine (`app/services/category_suggester.py`)**:
   - Rule-based natural language processing algorithm.
   - Scans ticket titles and descriptions for domain-specific keywords.
   - Suggests categories (`Hardware`, `Software`, `Network`, `Account`, `Email`) with high confidence score.

4. **Admin ITSM Controller (`app/routes/admin.py`)**:
   - State machine enforcement for ticket lifecycles (`Open` -> `Assigned` -> `In Progress` -> `Resolved` -> `Closed`).
   - Admin assignment and priority adjustments.

5. **Reporting & Analytics Engine (`app/routes/reports.py`)**:
   - Aggregated status, category, and priority volume breakdown.
   - Streamed CSV export for ITSM auditing.
