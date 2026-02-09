import uuid
from typing import List
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    patient_appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="patient",
        foreign_keys="Appointment.patient_id"
    )

    provider_appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="provider",
        foreign_keys="Appointment.provider_id"
    )

    provider_services: Mapped[list["ProviderService"]] = relationship(
        back_populates="provider"
    )

    availabilities: Mapped[list["Availability"]] = relationship(
        back_populates="provider",
        cascade="all, delete-orphan"
    )