import uuid
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db   
from typing import List
from app.models.service import Service
from app.schema.service_schema import *
from app.core.security import get_authenticated_user,require_admin

router = APIRouter(tags=["services"], prefix="/services")

@router.get("/list-service", response_model=List[ServiceResponseSchema])
async def list_service(db: AsyncSession = Depends(get_db), user=Depends(get_authenticated_user)):
    if user.role == "admin":
        result = await db.execute(select(Service))
    else:
        result = await db.execute(select(Service).where(Service.is_active == True))
    return result.scalars().all()
        
@router.post("/create-service")
async def create_service(request: ServiceCreateSchema,db: AsyncSession = Depends(get_db), admin=Depends(require_admin)):
    
    result = await db.execute(select(Service).where(Service.name == request.name.lower()))
    service = result.scalar_one_or_none()
    if service:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="service already exists")
    service = Service(
        name=request.name,
        description=request.description,
        is_active=request.is_active,
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.get("/retrieve-service/{serviceID}", response_model=ServiceResponseSchema)
async def retrieve_service(
    serviceID: uuid.UUID,
    db: AsyncSession = Depends(get_db), 
    user=Depends(get_authenticated_user),
):
    
    result = await db.execute(select(Service).where(Service.id == serviceID))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return service


@router.put("/update-service/{serviceID}", response_model=ServiceResponseSchema)
async def update_service(
    serviceID: uuid.UUID ,
    request: ServiceUpdateSchema,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Service).where(Service.id == serviceID))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    service.name = request.name
    service.description = request.description
    service.is_active = request.is_active
    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/delete-service/{serviceID}")
async def delete_service(    
    serviceID:uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Service).where(Service.id == serviceID))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    await db.delete(service)
    await db.commit()
    return JSONResponse(
            content={"message": "service successfully deleted"},
            status_code=status.HTTP_200_OK,
        )