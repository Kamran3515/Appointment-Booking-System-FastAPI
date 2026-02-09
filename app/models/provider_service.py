import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

class ProviderService(Base):
    __tablename__ = "provider_services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE")
    )

    price: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())


    provider: Mapped["User"] = relationship(
        back_populates="provider_services"
    )
    service: Mapped["Service"] = relationship(
        back_populates="provider_services"
    )
