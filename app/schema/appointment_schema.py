import uuid
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class AppointmentStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"

class AppointmentBaseSchema(BaseModel):
    service_id: uuid.UUID
    provider_id: uuid.UUID
    start_time: datetime
    end_time: datetime

class AppointmentCreateSchema(AppointmentBaseSchema):
    pass

class AppointmentUpdateSchema(BaseModel):
    status: AppointmentStatus = Field(default=AppointmentStatus.pending)

class AppointmentResponseSchema(AppointmentBaseSchema):
    id : uuid.UUID
    patient_id: uuid.UUID
    status: AppointmentStatus
    created_at: datetime

    class Config:
        from_attributes = True
