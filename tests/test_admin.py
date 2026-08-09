from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User, Ticket
from app.auth import hash_password

client = TestClient(app, raise_server_exceptions=False)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    admin = User(name="Admin User", email="admin@serviceflow.com", password_hash=hash_password("admin123"), role="admin")
    u1 = User(name="Regular User", email="user@example.com", password_hash=hash_password("user123"), role="user")
    db.add_all([admin, u1])
    db.commit()

    ticket = Ticket(
        title="Printer Paper Jam",
        description="Printer on 2nd floor has paper jam error",
        category="Hardware",
        priority="Medium",
        status="Open",
        user_id=u1.id
    )
    db.add(ticket)
    db.commit()
    db.close()


def test_admin_can_view_all_tickets():
    session = TestClient(app)
    session.post("/auth/login", data={"email": "admin@serviceflow.com", "password": "admin123"})

    response = session.get("/admin/tickets")
    assert response.status_code == 200
    assert "Printer Paper Jam" in response.text


def test_admin_status_transition_rules():
    session = TestClient(app)
    session.post("/auth/login", data={"email": "admin@serviceflow.com", "password": "admin123"})

    # Valid transition: Open -> Assigned
    resp1 = session.post("/admin/tickets/1/status", data={"new_status": "Assigned"}, follow_redirects=False)
    assert resp1.status_code == 303

    db = SessionLocal()
    t = db.query(Ticket).filter(Ticket.id == 1).first()
    assert t.status == "Assigned"

    # Invalid transition: Assigned -> Resolved directly (Must go to In Progress first)
    resp2 = session.post("/admin/tickets/1/status", data={"new_status": "Resolved"}, follow_redirects=False)
    assert resp2.status_code == 303
    assert "error=" in resp2.headers["location"]

    # Verify status did not change to Resolved
    db.refresh(t)
    assert t.status == "Assigned"
    db.close()


def test_admin_export_csv_report():
    session = TestClient(app)
    session.post("/auth/login", data={"email": "admin@serviceflow.com", "password": "admin123"})

    response = session.get("/admin/reports/export-csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "Ticket ID,Title,Category,Priority,Status" in response.text
    assert "Printer Paper Jam" in response.text
