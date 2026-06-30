from jose import jwt, JWTError
from datetime import datetime
import uuid
from pwdlib import PasswordHash
from app.config import settings
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.Auth.Auth_Schema import TokenData
from sqlalchemy import select
from app.Database.Models import User
from app.Database.database import get_db
from datetime import timedelta,timezone
import secrets
import hashlib
password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)

# hash_password
def hash_password(password: str) -> str:
    return password_hash.hash(password)
# verify_password
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)
# create_access_token
def create_access_token(user_id: str, role: str, expires_delta: Optional[timedelta] = None) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {
        "sub": str(user_id),
        "role": role,
        "token_type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4())
    }
    token= jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token,expire
# create_refresh_token
def create_refresh_token(user_id: int, role: str) -> tuple[str, datetime]:
    """Returns (encoded_jwt, expiry_datetime)"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

    payload = {
        "sub": str(user_id),
        "role": role,
        "token_type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token, expire
# decode_token
def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return TokenData(**payload)
    except jwt.JWTError as e:
        if isinstance(e, jwt.ExpiredSignatureError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
# get_current_user
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    token_data = decode_token(token)
    user_id = token_data.sub
    role = token_data.role
    result = await db.execute(select(User).where(User.id == user_id))

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user
# require_student
def require_student(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Student role required",
        )
    return current_user
# require_recruiter
def require_recruiter(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Recruiter role required",
        )
    return current_user


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

