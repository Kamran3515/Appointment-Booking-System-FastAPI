import uuid
from pydantic import BaseModel, Field, field_validator, EmailStr
from enum import Enum
from datetime import datetime


class ServiceBaseSchema(BaseModel):
    name: str = Field(..., max_length=100, description="name of the service")
    description: str | None = Field(None, max_length=255, description="description of the service")
    is_active: bool = Field(default=True, description="status of the service")

class ServiceCreateSchema(ServiceBaseSchema):
    pass

class ServiceUpdateSchema(ServiceBaseSchema):
    pass

class ServiceResponseSchema(ServiceBaseSchema):
    id : uuid.UUID
    created_at: datetime
    class Config:
        from_attributes = True