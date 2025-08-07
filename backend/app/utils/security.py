from cryptography.fernet import Fernet
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from config import settings
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from fastapi import Depends, HTTPException, status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT authentication
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Content encryption
def generate_encryption_key() -> bytes:
    return Fernet.generate_key()

def encrypt_content(content: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(content.encode())

def decrypt_content(encrypted_content: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_content).decode()

def get_user_key(user_id: str) -> bytes:
    """Get user-specific encryption key (simplified)"""
    # In production, fetch from secure storage
    return settings.MASTER_ENCRYPTION_KEY

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return {"id": user_id}
    except jwt.JWTError:
        raise credentials_exception

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
