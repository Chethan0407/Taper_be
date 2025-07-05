from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import UserCreate, UserOut, Token, LoginRequest, ForgotPasswordRequest
from app.services import auth as auth_service, email as email_service
from app.db.session import get_db
from app.utils.security import get_current_user

router = APIRouter()

@router.post("/signup", response_model=UserOut)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    user = auth_service.create_user(db, user_in)
    return user

@router.post("/login", response_model=Token)
def login(login_in: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, login_in.email, login_in.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = auth_service.reset_password(db, req.email, req.new_password)
    return {"msg": "Password reset successful"}

@router.get("/profile", response_model=UserOut)
def profile(current_user: UserOut = Depends(get_current_user)):
    return current_user

@router.post("/login/google")
def login_google():
    """Google SSO login (placeholder)."""
    return {"msg": "Google login"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: UserOut = Depends(get_current_user)):
    """Get current user info (returns user profile)."""
    return current_user

@router.post("/logout")
def logout():
    """Logout (placeholder)."""
    return {"msg": "Logged out"}

@router.post("/refresh-token")
def refresh_token():
    """Refresh JWT token (placeholder)."""
    return {"msg": "Token refreshed"}

@router.post("/request-password-reset")
def request_password_reset(
    background_tasks: BackgroundTasks,
    email: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    user = auth_service.get_user_by_email(db, email)
    if not user:
        # Don't reveal if user exists
        return {"msg": "If the email exists, a reset link will be sent."}
    token = auth_service.create_password_reset_token({"sub": user.email})
    reset_link = f"http://localhost:5173/reset-password?token={token}"
    background_tasks.add_task(
        email_service.send_reset_email,
        to_email=user.email,
        reset_link=reset_link
    )
    return {"msg": "If the email exists, a reset link will be sent."}

@router.post("/reset-password")
def reset_password_with_token(
    token: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    email = auth_service.verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = auth_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    auth_service.reset_password(db, email, new_password)
    return {"msg": "Password reset successful"} 