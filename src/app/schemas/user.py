from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """
    Base user schema with common attributes
    """

    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """
    Schema for creating a new user
    """

    password: str


class UserUpdate(BaseModel):
    """
    Schema for updating user information
    """

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    """
    Base schema for user stored in database
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class User(UserInDBBase):
    """
    Schema for user returned to API client
    """

    pass


class UserInDB(UserInDBBase):
    """
    Schema for user stored in database including hashed password
    """

    hashed_password: str
