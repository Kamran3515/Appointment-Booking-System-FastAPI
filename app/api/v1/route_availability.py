import uuid
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db   
from typing import List
from app.models.availability import Availability
from app.schema.availability_schema import *
from app.core.security import get_authenticated_user,require_admin

router = APIRouter(tags=["availability"], prefix="/availability")

@router.get("/list-availability", response_model=List[AvailabilityResponseSchema])
async def list_availability(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
):
    stmt = select(Availability)

    if user.role == "client":
        stmt = stmt.where(Availability.is_available == True)
    elif user.role == "provider":
        stmt = stmt.where(Availability.provider_id == user.id)

    result = await db.execute(stmt)
    return result.scalars().all()

        
@router.post("/create-availability", response_model=AvailabilityResponseSchema)
async def create_availability(
    request: AvailabilityCreateSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
):
    if user.role == "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have no permission"
        )

    if request.start_time >= request.end_time:
        raise HTTPException(
            status_code=400,
            detail="start_time must be before end_time"
        )

    if user.role == "admin":
        provider_id = request.provider_id
    else:  # provider
        provider_id = user.id

    availability = Availability(
        provider_id=provider_id,
        start_time=request.start_time,
        end_time=request.end_time,
        is_available=True,
    )

    db.add(availability)
    await db.commit()
    await db.refresh(availability)
    return availability


@router.get("/retrieve-availability/{availabilityID}", response_model=AvailabilityResponseSchema)
async def retrieve_availability(
    availabilityID: uuid.UUID,
    db: AsyncSession = Depends(get_db), 
    user=Depends(get_authenticated_user),
):
    
    result = await db.execute(
        select(Availability).where(Availability.id == availabilityID)
    )
    availability = result.scalar_one_or_none()

    if not availability:
        raise HTTPException(404, "availability not found")

    if user.role == "provider" and availability.provider_id != user.id:
        raise HTTPException(403, "You have no permission")

    if user.role == "client" and not availability.is_available:
        raise HTTPException(403, "You have no permission")

    return availability


@router.put("/update-availability/{availabilityID}", response_model=AvailabilityResponseSchema)
async def update_availability(
    availabilityID: uuid.UUID ,
    request: AvailabilityUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
):
    if user.role == "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have no permission"
        )
    result = await db.execute(select(Availability).where(Availability.id == availabilityID))
    availability = result.scalar_one_or_none()
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="availability not found")

    if user.role == "provider" and availability.provider_id != user.id:
        raise HTTPException(403, "You have no permission")

    if request.start_time >= request.end_time:
        raise HTTPException(
            status_code=400,
            detail="start_time must be before end_time"
        )

    if user.role == "admin":
        provider_id = request.provider_id
    else:  # provider
        provider_id = user.id

    availability.provider_id=provider_id
    availability.start_time=request.start_time
    availability.end_time=request.end_time
    availability.is_available=True

    await db.commit()
    await db.refresh(availability)
    return availability



@router.delete("/delete-availability/{availabilityID}")
async def delete_availability(    
    availabilityID:uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
):
    if user.role == "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have no permission"
        )
    result = await db.execute(
        select(Availability).where(Availability.id == availabilityID)
    )
    availability = result.scalar_one_or_none()

    if not availability:
        raise HTTPException(404, "Availability not found")

    if user.role == "provider" and availability.provider_id != user.id:
        raise HTTPException(403, "You have no permission")

    availability.is_available = False
    await db.commit()

    return JSONResponse(
            content={"message": "Availability disabled successfully"},
            status_code=status.HTTP_200_OK,
        )