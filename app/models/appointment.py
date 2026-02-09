import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False
    )

    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    patient: Mapped["User"] = relationship(
        back_populates="patient_appointments",
        foreign_keys=[patient_id]
    )

    provider: Mapped["User"] = relationship(
        back_populates="provider_appointments",
        foreign_keys=[provider_id]
    )

    service: Mapped["Service"] = relationship(
        back_populates="appointments",
    )