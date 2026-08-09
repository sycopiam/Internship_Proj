import sys
from datetime import datetime, timedelta, timezone
from app.database import Base, engine, SessionLocal
from app.models import User, Ticket
from app.auth import hash_password


def seed_database():
    print("Initializing database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("Seeding Users...")
        # 1 Admin
        admin_user = User(
            name="System Administrator",
            email="admin@serviceflow.com",
            password_hash=hash_password("admin123"),
            role="admin"
        )

        # 2 Standard Users
        user1 = User(
            name="John Doe",
            email="john.doe@company.com",
            password_hash=hash_password("user123"),
            role="user"
        )

        user2 = User(
            name="Jane Smith",
            email="jane.smith@company.com",
            password_hash=hash_password("user123"),
            role="user"
        )

        db.add_all([admin_user, user1, user2])
        db.commit()

        # Refresh to get assigned IDs
        db.refresh(admin_user)
        db.refresh(user1)
        db.refresh(user2)

        print(f"Users created: Admin ID={admin_user.id}, User1 ID={user1.id}, User2 ID={user2.id}")

        print("Seeding Sample Tickets...")
        now = datetime.now(timezone.utc)

        tickets = [
            Ticket(
                title="WiFi Connection Drops Frequently in East Wing",
                description="The wireless network connection keeps dropping every 15 minutes when sitting in the East Wing conference room. Requires router check.",
                category="Network",
                priority="High",
                status="In Progress",
                created_at=now - timedelta(days=3),
                updated_at=now - timedelta(days=1),
                user_id=user1.id,
                assigned_to=admin_user.id
            ),
            Ticket(
                title="Laptop Screen Flicker and Dimming",
                description="Dell laptop screen is flickering uncontrollably when plugged into power. Need hardware replacement or display driver check.",
                category="Hardware",
                priority="Critical",
                status="Assigned",
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(hours=12),
                user_id=user1.id,
                assigned_to=admin_user.id
            ),
            Ticket(
                title="Forgot Account Password After Vacation",
                description="I cannot log in to my domain account after returning from leave. Please reset my account password.",
                category="Account",
                priority="Medium",
                status="Resolved",
                created_at=now - timedelta(days=5),
                updated_at=now - timedelta(days=4),
                user_id=user1.id,
                assigned_to=admin_user.id
            ),
            Ticket(
                title="Outlook Email Attachment Sync Error",
                description="Microsoft Outlook fails to download PDF email attachments, showing error code 0x8004010F.",
                category="Email",
                priority="Medium",
                status="Open",
                created_at=now - timedelta(hours=6),
                updated_at=now - timedelta(hours=6),
                user_id=user2.id,
                assigned_to=None
            ),
            Ticket(
                title="Internal CRM Application Keeps Crashing",
                description="Whenever I try to export sales reports, the CRM app freezes and crashes silently.",
                category="Software",
                priority="High",
                status="Open",
                created_at=now - timedelta(hours=2),
                updated_at=now - timedelta(hours=2),
                user_id=user2.id,
                assigned_to=None
            ),
            Ticket(
                title="Request for Dual Monitor Extension Cable",
                description="Need a DisplayPort to HDMI cable for setting up workstation dual monitors.",
                category="Hardware",
                priority="Low",
                status="Closed",
                created_at=now - timedelta(days=10),
                updated_at=now - timedelta(days=7),
                user_id=user2.id,
                assigned_to=admin_user.id
            )
        ]

        db.add_all(tickets)
        db.commit()

        print(f"Successfully seeded {len(tickets)} sample tickets!")
        print("Default Credentials:")
        print("  Admin: admin@serviceflow.com / admin123")
        print("  User 1: john.doe@company.com / user123")
        print("  User 2: jane.smith@company.com / user123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
