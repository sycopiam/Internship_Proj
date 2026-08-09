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
    # Create two users
    u1 = User(name="User One", email="user1@example.com", password_hash=hash_password("user123"), role="user")
    u2 = User(name="User Two", email="user2@example.com", password_hash=hash_password("user123"), role="user")
    db.add_all([u1, u2])
    db.commit()

    # User 1 creates a ticket
    t1 = Ticket(title="User 1 Monitor Issue", description="Monitor flickering", category="Hardware", priority="High", status="Open", user_id=u1.id)
    db.add(t1)
    db.commit()
    db.close()


def test_ticket_creation_by_user():
    # Login as User 1
    session = TestClient(app)
    session.post("/auth/login", data={"email": "user1@example.com", "password": "user123"})

    response = session.post(
        "/tickets/create",
        data={
            "title": "VPN Disconnected",
            "description": "VPN connection drops repeatedly when remote",
            "category": "Network",
            "priority": "High"
        },
        follow_redirects=False
    )
    assert response.status_code == 303

    db = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.title == "VPN Disconnected").first()
    assert ticket is not None
    assert ticket.category == "Network"
    assert ticket.status == "Open"
    db.close()


def test_user_cannot_access_other_user_ticket():
    # Login as User 2
    session_u2 = TestClient(app, raise_server_exceptions=False)
    session_u2.post("/auth/login", data={"email": "user2@example.com", "password": "user123"})

    # Try to access User 1's ticket (Ticket ID = 1)
    response = session_u2.get("/tickets/1")
    assert response.status_code == 403
    assert "Access Denied" in response.text
