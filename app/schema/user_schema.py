import uuid
from pydantic import BaseModel, Field, field_validator, EmailStr
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    client = "client"
    provider = "provider"
    admin = "admin"

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...,max_length=250, description="email of the user")
    password: str = Field(..., description="password of the user")


class UserRegisterSchema(BaseModel):
    full_name: str = Field(
        ..., max_length=250, min_length=5, description="full name of the user"
    )
    role: UserRole = Field(default=UserRole.client, description="user role (client|provider|admin)")
    email: EmailStr = Field(...,max_length=250, description="email of the user")
    password: str = Field(..., description="password of the user")
    password_confirm: str = Field(
        ..., description="confirm password of the user"
    )

    @field_validator("password_confirm")
    def check_password_match(cls, password_confirm, validation):
        if not (password_confirm == validation.data.get("password")):
            raise ValueError("password doesn't match")
        return password_confirm
    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v


class UserRefreshTokenSchema(BaseModel):
    token: str = Field(
        ..., description="refresh token for receive access token"
    )

class UserBaseSchema(BaseModel):
    full_name: str = Field(
        ..., max_length=250, min_length=5, description="username of the user"
    )
    email: EmailStr = Field(...,max_length=250, description="email of the user")
    password: str = Field(..., description="password of the user")


class UserUpdateSchema(UserBaseSchema):
    pass

class UserResponseSchema(UserBaseSchema):
    id: uuid.UUID
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True
