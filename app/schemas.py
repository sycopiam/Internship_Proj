from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# --- User Schemas ---
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Ticket Schemas ---
class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5)
    category: str
    priority: str = "Medium"


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    user_id: int
    assigned_to: Optional[int] = None

    class Config:
        from_attributes = True


# --- Intelligent Category Suggestion Schemas ---
class CategorySuggestRequest(BaseModel):
    description: str


class CategorySuggestResponse(BaseModel):
    suggested_category: str
    confidence: str
    matched_keywords: List[str]
