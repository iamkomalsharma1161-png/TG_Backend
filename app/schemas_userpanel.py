from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    full_name: str
    email_address: EmailStr
    contact_number: str
    password: str

class UserLogin(BaseModel):
    login_id: str  # Can be email or phone
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    profile_photo_url: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    email_address: str
    contact_number: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    profile_photo_url: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class SupportQueryCreate(BaseModel):
    subject: str
    query_text: str
    photo_url: Optional[str] = None

class SupportQueryResponse(BaseModel):
    id: int
    subject: str
    query_text: str
    photo_url: Optional[str]
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True
