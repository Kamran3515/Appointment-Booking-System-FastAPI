import uuid
from datetime import datetime
from sqlalchemy import Boolean, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    provider_services: Mapped[list["ProviderService"]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan"
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan"
    )
