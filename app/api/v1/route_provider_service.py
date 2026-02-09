import uuid
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db   
from typing import List
from app.models.provider_service import ProviderService
from app.models.user import User
from app.models.service import Service
from app.schema.provider_service_schema import *
from app.core.security import get_authenticated_user

router = APIRouter(tags=["provider-services"], prefix="/provider-services")

@router.get("/list-provider-service", response_model=List[ProviderServiceResponseSchema])
async def list_service(db: AsyncSession = Depends(get_db), user=Depends(get_authenticated_user)):
    if user.role == "admin":
        result = await db.execute(select(ProviderService))
    else:
        result = await db.execute(select(ProviderService)
                                  .join(User)
                                  .join(Service)
                                  .where(ProviderService.is_active == True,User.is_active == True,Service.is_active == True)
                                )
    return result.scalars().all()
        
@router.post("/create-provider-service")
async def create_service(
    request: ProviderServiceCreateSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user)
):
    if user.role != "client":
        result = await db.execute(select(ProviderService)
                                  .where(ProviderService.provider_id == user.id,
                                         ProviderService.service_id == request.service_id))
        provider_service = result.scalar_one_or_none()
        if provider_service:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="provider-service already exists")
        elif user.role == "provider":
            provider_id = user.id
        else:
            provider_id = request.provider_id,

        provider_service = ProviderService(
            provider_id = provider_id,
            service_id = request.service_id,
            price=request.price,
            duration_minutes=request.duration_minutes,
            is_active=request.is_active,
        )

        db.add(provider_service)
        await db.commit()
        await db.refresh(provider_service)
        return provider_service
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you have not permission")


@router.get("/retrieve-provider-service/{ProviderServiceID}", response_model=ProviderServiceResponseSchema)
async def retrieve_service(
    ProviderServiceID: uuid.UUID,
    db: AsyncSession = Depends(get_db), 
    user=Depends(get_authenticated_user),
):
    
    result = await db.execute(select(ProviderService).where(ProviderService.id == ProviderServiceID))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return service


@router.put("/update-provider-service/{ProviderServiceID}", response_model=ProviderServiceResponseSchema)
async def update_provider_service(
    ProviderServiceID: uuid.UUID ,
    request: ProviderServiceUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
):
    if user.role == "client":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you have not permission")
    
    result = await db.execute(select(ProviderService).where(ProviderService.id == ProviderServiceID))
    provider_service = result.scalar_one_or_none()

    if not provider_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="provider-service not found")
    
    if user.role == "admin":
        provider_service.provider_id = request.provider_id
    elif user.role == "provider" and user.id != provider_service.provider_id:
        raise HTTPException(status_code=status.HTTP_404_FORBIDDEN, detail="you have not permission")
    else:
        provider_service.provider_id = user.id
    provider_service.service_id = request.service_id
    provider_service.price=request.price
    provider_service.duration_minutes=request.duration_minutes
    provider_service.is_active=request.is_active
    await db.commit()
    await db.refresh(provider_service)
    return provider_service


@router.delete("/delete-provider-service/{ProviderServiceID}")
async def delete_provider_service(    
    ProviderServiceID:uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
):
    if user.role != "client":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you have not permission")
    result = await db.execute(select(ProviderService).where(ProviderService.id == ProviderServiceID))
    provider_service = result.scalar_one_or_none()
    if not provider_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="provider-service not found")
    if user.role == "provider" and user.id != provider_service.provider_id:    
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you have not permission")
    
    provider_service.is_active = False
    await db.commit()
    return JSONResponse(
        content={"message": "service successfully deleted"},
        status_code=status.HTTP_200_OK,
    )
    