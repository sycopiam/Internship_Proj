from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # "user" or "admin"
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    created_tickets = relationship("Ticket", foreign_keys="Ticket.user_id", back_populates="creator", cascade="all, delete-orphan")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assigned_to", back_populates="assignee")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # Hardware, Software, Network, Account, Email, Other
    priority = Column(String(20), default="Medium", nullable=False)  # Low, Medium, High, Critical
    status = Column(String(20), default="Open", nullable=False)  # Open, Assigned, In Progress, Resolved, Closed
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[user_id], back_populates="created_tickets")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")

    def __repr__(self):
        return f"<Ticket #{self.id} {self.title} [{self.status}]>"
