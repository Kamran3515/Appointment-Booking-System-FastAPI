import jwt
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.core.config import settings
from jwt import ExpiredSignatureError, DecodeError
from fastapi import Depends, HTTPException, status
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.models.user import User

security = HTTPBearer()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        if payload.get("type") != "access":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return user

    except ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except DecodeError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token invalid")
    except Exception as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=f"Authentications failed, {e}")

# ساخت توکن
def generate_access_token(user_id: uuid.UUID, expires_in: int = 60 * 5) -> str:
    now = datetime.utcnow()
    payload = {
        "type": "access",
        "user_id": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user_id: int, expires_in: int = 3600 * 24) -> str:
    now = datetime.utcnow()
    payload = {
        "type": "refresh",
        "user_id": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_refresh_token(token: str) -> uuid.UUID:
    try:
        decode = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if decode.get("type") != "refresh":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token type invalid")
        return uuid.UUID(decode["user_id"])
    except (ExpiredSignatureError, DecodeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def require_admin(user: User = Depends(get_authenticated_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403)
    return user