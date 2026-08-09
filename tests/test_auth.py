from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import User

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_user_registration():
    response = client.post(
        "/auth/register",
        data={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "password123"
        },
        follow_redirects=False
    )
    assert response.status_code == 303
    assert "/dashboard" in response.headers["location"]

    # Verify user saved in DB
    db = SessionLocal()
    user = db.query(User).filter(User.email == "testuser@example.com").first()
    assert user is not None
    assert user.name == "Test User"
    assert user.role == "user"
    db.close()


def test_duplicate_registration_fails():
    client.post(
        "/auth/register",
        data={"name": "User One", "email": "dup@example.com", "password": "password123"}
    )
    # Attempting duplicate registration
    response = client.post(
        "/auth/register",
        data={"name": "User Two", "email": "dup@example.com", "password": "password123"}
    )
    assert response.status_code == 400
    assert "already exists" in response.text


def test_login_success_and_failure():
    # Register user
    client.post(
        "/auth/register",
        data={"name": "Login User", "email": "login@example.com", "password": "securepassword"}
    )

    # Invalid password login
    bad_login = client.post(
        "/auth/login",
        data={"email": "login@example.com", "password": "wrongpassword"}
    )
    assert bad_login.status_code == 400
    assert "Invalid email or password" in bad_login.text

    # Valid password login
    good_login = client.post(
        "/auth/login",
        data={"email": "login@example.com", "password": "securepassword"},
        follow_redirects=False
    )
    assert good_login.status_code == 303
    assert "/dashboard" in good_login.headers["location"]
