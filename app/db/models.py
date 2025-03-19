from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


# Shared properties
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool = True
    role: UserRole = UserRole.USER
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    notification_email: bool = True
    notification_push: bool = True
    theme: Optional[str] = None
    language: Optional[str] = None
    phone: str


# Properties to receive via API on creation
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    phone: str


# Properties to receive via API on update
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


# Properties to return via API
class UserOut(BaseModel):
    id: str
    email: str
    name: str
    phone: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


# Generic message
class Message(BaseModel):
    to: str
    text: str


# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: Optional[int] = None


class NewPassword(BaseModel):
    token: str
    new_password: str


class MessageType(str, Enum):
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"
    BALANCE = "BALANCE"
    STATEMENT = "STATEMENT"
    CATEGORIES = "CATEGORIES"
    REPORT = "REPORT"
    CATEGORY_REPORT = "CATEGORY_REPORT"
    EDIT = "EDIT"

    @classmethod
    def _missing_(cls, value):
        return cls(value.upper()) if isinstance(value, str) else None


class WhatsAppMessage(BaseModel):
    type: MessageType
    amount: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    phone: str
    user_id: str
    period: Optional[str] = None

    model_config = {
        "use_enum_values": True,
        "from_attributes": True
    }


class ProfileCreate(BaseModel):
    phone: str = Field(
        ...,
        description="Phone number in international format",
        example="5511953238980"
    )
    
    model_config = {
        "from_attributes": True
    }


class ProfileOut(BaseModel):
    id: str
    phone: str
    full_name: str
    email: str
    created_at: datetime
    updated_at: datetime


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class TransactionOut(BaseModel):
    id: str
    user_id: str
    amount: Decimal
    description: Optional[str]
    category: str
    type: TransactionType
    date: datetime
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class CategoryOut(BaseModel):
    id: str
    user_id: str
    name: str
    type: str
    icon: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: str


class TransactionCreate(BaseModel):
    amount: Decimal
    description: str
    category: str
    type: TransactionType
    date: datetime


class TransactionResponse(BaseModel):
    id: str
    amount: Decimal
    description: str
    category: str
    type: str
    date: datetime
    created_at: datetime
