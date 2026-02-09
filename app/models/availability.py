import uuid
from datetime import time,datetime

from sqlalchemy import DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Availability(Base):
    __tablename__ = "availabilities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    start_time: Mapped[time] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    end_time: Mapped[time] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    provider: Mapped["User"] = relationship(
        back_populates="availabilities"
    )
