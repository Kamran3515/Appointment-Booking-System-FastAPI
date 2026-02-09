import email
from sqlalchemy import select
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from typing import List
from app.models.user import User
from app.schema.user_schema import *
from app.core.security import get_authenticated_user,hash_password,verify_password
from app.schema.user_schema import (
    UserLoginSchema,
    UserRegisterSchema,
    UserRefreshTokenSchema,
)

from app.core.security import (
    generate_access_token,
    generate_refresh_token,
    decode_refresh_token,
    get_authenticated_user
)

router = APIRouter(tags=["Authentications"], prefix="/auth")


@router.post("/register",response_model=UserResponseSchema)
async def user_register(
    request: UserRegisterSchema, db: AsyncSession = Depends(get_db)
):
    email = request.email.lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if (user):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Your email is used before",
        )

    try:
        user_obj = User(
            full_name=request.full_name.lower(),
            email=request.email.lower(),
            role=request.role.lower(),
            password_hash= hash_password(request.password),
            is_superuser=request.role == "admin",
        )

        db.add(user_obj)
        await db.commit()
        await db.refresh(user_obj)

    except Exception:
        await db.rollback()
        raise

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"detail": "user registered successfully"},
    )

@router.post("/login")
async def user_login(request: UserLoginSchema, db: AsyncSession = Depends(get_db)):
    email = request.email.lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user doesn't exists",
        )
    if not verify_password(request.password,user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="password invalid"
        )
    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "detail": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    )


@router.post("/refresh-token")
def user_refresh_token(
    request: UserRefreshTokenSchema, db: AsyncSession = Depends(get_db)
):
    user_id = decode_refresh_token(request.token)
    access_token = generate_access_token(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "Login successful", "access_token": access_token},
    )
