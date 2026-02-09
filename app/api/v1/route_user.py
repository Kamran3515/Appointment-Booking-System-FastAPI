import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from typing import List
from app.models.user import User
from app.schema.user_schema import *
from app.core.security import hash_password
from app.core.security import get_authenticated_user,require_admin

router = APIRouter(tags=["users"], prefix="/users")


@router.get("/list-user", response_model=List[UserBaseSchema])
async def list_user(
    db: AsyncSession = Depends(get_db),
    admin_user=Depends(require_admin),
):

    if admin_user:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return users


@router.get("/{userID}", response_model=UserResponseSchema)
async def retrieve_user(
    userID: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
):
    if user.role == "admin":
        result = await db.execute(select(User).where(User.id == userID))
        user_target = result.scalar_one_or_none()
        if not user_target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    else:
        if user.id != userID:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to do that.")
        result = await db.execute(select(User).where(User.id == user.id))
        user_target = result.scalar_one_or_none()

    return user_target

@router.put(
        "/{userID}",    
        status_code=status.HTTP_200_OK,
        response_model=UserResponseSchema
)
async def update_user(
    userID: uuid.UUID,
    request: UserUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
):
    if user.role == "admin":
        result = await db.execute(select(User).where(User.id == userID))
        user_target = result.scalar_one_or_none()
        if not user_target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    else:
        if user.id != userID:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to do that.")
        result = await db.execute(select(User).where(User.id == user.id))
        user_target = result.scalar_one_or_none()

    exists = await db.execute(select(User).where(User.email == request.email, User.id != user_target.id))

    if exists.scalar_one_or_none():
        raise HTTPException(409, "Email already exists")

    user_target.full_name=request.full_name
    user_target.email=request.email
    user_target.password_hash=hash_password(request.password)

    await db.commit()
    await db.refresh(user_target)
    return user_target

@router.delete("/{userID}", status_code=status.HTTP_200_OK)
async def delete_user(
    userID: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
):
    if user.role == "admin":
        result = await db.execute(select(User).where(User.id == userID))
        user_target = result.scalar_one_or_none()
        if not user_target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    else:
        if user.id != userID:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to do that.")
        result = await db.execute(select(User).where(User.id == user.id))
        user_target = result.scalar_one_or_none()

    user_target.is_active = False
    await db.commit()
    return JSONResponse(
        content={"message": "user successfully deactivated"},
        status_code=status.HTTP_200_OK,
    )
