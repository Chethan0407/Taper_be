from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db import models
from app.schemas.user import UserCreate
from app.utils import security
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os

RESET_SECRET_KEY = os.environ.get("RESET_SECRET_KEY", "super-secret-reset-key")
RESET_TOKEN_EXPIRE_MINUTES = 60

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_in: UserCreate):
    user = get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered. Please log in instead.")
    hashed_password = security.get_password_hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict):
    return security.create_access_token(data)

def reset_password(db: Session, email: str, new_password: str):
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = security.get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user

def create_password_reset_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, RESET_SECRET_KEY, algorithm="HS256")

def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, RESET_SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except JWTError:
        return None 