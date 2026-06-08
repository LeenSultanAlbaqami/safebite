"""
SafeBite — Security Layer
Direct bcrypt password hashing + JWT token creation & verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import bcrypt  # نستخدمها مباشرة الآن

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

SECRET_KEY  = os.getenv("SECRET_KEY",  "safebite-secret-change-me")
ALGORITHM   = os.getenv("ALGORITHM",   "HS256")
TOKEN_MINS  = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")


# ── Password helpers (Direct Bcrypt) ──────────────────────────────────────────
def hash_password(plain: str) -> str:
    # تحويل النص إلى bytes ثم التشفير ثم تحويل النتيجة لنص لتخزينها في القاعدة
    pwd_bytes = plain.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    # التحقق بمقارنة النص الصريح مع الهاشم المخزن
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


# ── JWT helpers ───────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=TOKEN_MINS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Dependency: current authenticated user ────────────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    user_id: str = str(payload.get("sub"))
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
