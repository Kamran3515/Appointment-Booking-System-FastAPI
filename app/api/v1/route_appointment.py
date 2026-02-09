import uuid
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.db.session import get_db
from app.models.appointment import Appointment
from app.models.availability import Availability
from app.models.provider_service import ProviderService
from app.schema.appointment_schema import *
from app.core.security import get_authenticated_user
from app.models.user import User

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.get("/", response_model=List[AppointmentResponseSchema])
async def list_appointments(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_authenticated_user),
):
    stmt = select(Appointment)

    if user.role == "client":
        stmt = stmt.where(Appointment.patient_id == user.id)
    elif user.role == "provider":
        stmt = stmt.where(Appointment.provider_id == user.id)
    # admin همه رو می‌بینه

    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=AppointmentResponseSchema)
async def create_appointment(
    request: AppointmentCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_authenticated_user),
):
    if user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can book appointments")

    if request.start_time >= request.end_time:
        raise HTTPException(status_code=400, detail="Invalid time range")

    # بررسی اینکه provider این سرویس رو ارائه میده
    result = await db.execute(
        select(ProviderService).where(
            ProviderService.provider_id == request.provider_id,
            ProviderService.service_id == request.service_id,
            ProviderService.is_active == True,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Provider does not offer this service")

    # بررسی availability
    result = await db.execute(
        select(Availability).where(
            Availability.provider_id == request.provider_id,
            Availability.is_available == True,
            Availability.start_time <= request.start_time,
            Availability.end_time >= request.end_time,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Provider not available at this time")

    # جلوگیری از overlap
    result = await db.execute(
        select(Appointment).where(
            Appointment.provider_id == request.provider_id,
            Appointment.status.in_(["pending", "confirmed"]),
            or_(
                and_(
                    Appointment.start_time <= request.start_time,
                    Appointment.end_time > request.start_time,
                ),
                and_(
                    Appointment.start_time < request.end_time,
                    Appointment.end_time >= request.end_time,
                ),
            ),
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Time slot already booked")

    appointment = Appointment(
        patient_id=user.id,
        provider_id=request.provider_id,
        service_id=request.service_id,
        start_time=request.start_time,
        end_time=request.end_time,
        status="pending",
    )

    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment

@router.get("/{appointment_id}", response_model=AppointmentResponseSchema)
async def retrieve_appointment(
    appointment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()

    if not appointment:
        raise HTTPException(404, "Appointment not found")

    if user.role != "admin" and user.id not in (
        appointment.patient_id,
        appointment.provider_id,
    ):
        raise HTTPException(403, "You have no permission")

    return appointment

@router.put("/{appointment_id}/status", response_model=AppointmentResponseSchema)
async def update_appointment_status(
    appointment_id: uuid.UUID,
    request: AppointmentUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()

    if not appointment:
        raise HTTPException(404, "Appointment not found")

    if user.role == "client":
        if appointment.patient_id != user.id or request.status != AppointmentStatus.cancelled:
            raise HTTPException(403, "Clients can only cancel their own appointments")

    elif user.role == "provider":
        if appointment.provider_id != user.id or request.status not in (
            AppointmentStatus.confirmed,
            AppointmentStatus.completed,
        ):
            raise HTTPException(403, "Invalid action")

    # admin همه چی می‌تونه

    appointment.status = request.status.value
    await db.commit()
    await db.refresh(appointment)
    return appointment

@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_authenticated_user),
):
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()

    if not appointment:
        raise HTTPException(404, "Appointment not found")

    if user.role != "admin" and appointment.patient_id != user.id:
        raise HTTPException(403, "You have no permission")

    appointment.status = "cancelled"
    await db.commit()

    return {"message": "Appointment cancelled successfully"}
