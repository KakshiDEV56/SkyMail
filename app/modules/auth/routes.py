from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.modules.auth.schemas import (
    CompanyRegisterRequest,
    CompanyLoginRequest,
    VerifyOTPRequest,
    RefreshTokenRequest,
)
from app.modules.auth.handlers.handler import RegisterHandler, LoginHandler
from app.utils.jwt_handler import verify_token, TokenPayload
from jose import JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database.database import get_db
from app.modules.auth.password_reset.service import PasswordResetService
from app.modules.auth.password_reset.schemas import PasswordResetRequest, PasswordResetVerify


router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()


async def get_current_company(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> str:
    token = credentials.credentials
    
    try:
        payload: TokenPayload = verify_token(token)
        company_id: str = payload.sub
        
        if company_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        return company_id
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new company",
    description="Register a new company account. OTP will be sent to the email."
)
async def register(
    request: CompanyRegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return await RegisterHandler.register(request, background_tasks, db)


@router.post(
    "/resend-otp",
    status_code=status.HTTP_200_OK,
    summary="Resend OTP",
    description="Resend OTP to registered email address."
)
async def resend_otp(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return await RegisterHandler.resend_otp(email, background_tasks, db)


@router.post(
    "/verify-otp",
    status_code=status.HTTP_200_OK,
    summary="Verify OTP and complete registration",
    description="Verify the OTP sent to email to complete company registration."
)
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    return await RegisterHandler.verify_otp(request, db)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    description="Authenticate company with email and password."
)
async def login(
    request: CompanyLoginRequest,
    db: Session = Depends(get_db)
):
    return await LoginHandler.login(request, db)


@router.post(
    "/refresh-token",
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Generate a new access token using refresh token."
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    return await LoginHandler.refresh_token(request, db)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Logout and revoke refresh tokens."
)
async def logout(
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await LoginHandler.logout(company_id, db)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get current company profile",
    description="Get details of the currently authenticated company."
)
async def get_profile(
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await LoginHandler.get_profile(company_id, db)

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset - sends OTP to email"""
    success, message = await PasswordResetService.request_password_reset(
        request.email, db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"message": message}


@router.post("/reset-password")
async def reset_password(
    request: PasswordResetVerify,
    db: Session = Depends(get_db)
):
    """Verify OTP and reset password"""
    success, message = await PasswordResetService.verify_reset_otp_and_update_password(
        request.email,
        request.otp,
        request.new_password,
        db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"message": message}
