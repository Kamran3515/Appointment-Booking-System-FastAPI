import uuid
from pydantic import BaseModel, Field, field_validator, EmailStr
from datetime import datetime,time


class AvaiabilityBaseSchema(BaseModel): 
    provider_id: uuid.UUID 
    end_time: time = Field(default=0)
    start_time: time = Field(default=0)
    is_available: bool = Field(default=True, description="status of the provider availability")

class AvailabilityCreateSchema(AvaiabilityBaseSchema):
    pass

class AvailabilityUpdateSchema(AvaiabilityBaseSchema):
    pass

class AvailabilityResponseSchema(AvaiabilityBaseSchema):
    id : uuid.UUID
    created_at: datetime
    class Config:
        from_attributes = True