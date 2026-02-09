import uuid
from pydantic import BaseModel, Field, field_validator, EmailStr
from datetime import datetime


class ProviderServiceBaseSchema(BaseModel):
    price: int = Field(default=0, gt=0, description="price of the provider service")
    duration_minutes: int = Field(default=0,ge=0, description="time of the provider service")
    is_active: bool = Field(default=True, description="status of the provider service")
    service_id: uuid.UUID 
    provider_id: uuid.UUID 

class ProviderServiceCreateSchema(ProviderServiceBaseSchema):
    pass

class ProviderServiceUpdateSchema(ProviderServiceBaseSchema):
    pass

class ProviderServiceResponseSchema(ProviderServiceBaseSchema):
    id : uuid.UUID
    created_at: datetime
    class Config:
        from_attributes = True