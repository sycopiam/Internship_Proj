# ServiceFlow - Testing Strategy & Execution Guide

## Overview
ServiceFlow incorporates automated unit testing using `pytest` and `httpx` / `starlette.testclient` to ensure application reliability, state-machine integrity, role isolation, and accurate rule-engine calculations.

## Test Suite Structure

The test suite is located in the `tests/` directory:

```
tests/
├── __init__.py
├── test_auth.py               # Authentication & Session Tests (Register, Duplicate Check, Login)
├── test_tickets.py            # User Ticket Operations & Isolation Guard Tests
├── test_admin.py               # Admin Management, State Transitions, & CSV Export Tests
└── test_category_suggester.py # Rule-Based Category Suggester Unit Tests
```

## Test Coverage Summary

| Module | Test File | Cases Tested |
| :--- | :--- | :--- |
| **Authentication** | `tests/test_auth.py` | - User registration<br>- Duplicate email prevention<br>- Login with valid credentials<br>- Login rejection on invalid password |
| **Tickets & Security** | `tests/test_tickets.py` | - User ticket creation<br>- Category & priority default assignment<br>- Strict isolation: User A blocked from viewing User B tickets (403 Forbidden) |
| **Admin & Workflow** | `tests/test_admin.py` | - Admin ticket overview<br>- Ticket status state machine validation (`Open` -> `Assigned` -> `In Progress`)<br>- Prevention of illegal jumps (e.g. `Assigned` directly to `Resolved`)<br>- CSV report generation and header format verification |
| **Rule Engine** | `tests/test_category_suggester.py` | - Keyword detection (`WiFi` -> `Network`, `Laptop` -> `Hardware`, `Password` -> `Account`, `Outlook` -> `Email`, `Crash` -> `Software`) |

## Running Tests

To run the full automated test suite:

```bash
pytest
```

To run with verbose output and individual test names:

```bash
pytest -v
```

To run a specific test module:

```bash
pytest tests/test_tickets.py
```
