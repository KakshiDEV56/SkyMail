from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.modules.auth.routes import get_current_company
from app.modules.auth.profile.service import CompanyProfileService
from app.modules.auth.profile.schemas import (
    CompanyProfileResponse,
    CompanyProfileUpdateRequest,
    CompanyProfileImageResponse
)

router = APIRouter(prefix="/api/auth", tags=["Company Profile"])


@router.get("/profile")
async def get_profile(
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
) -> CompanyProfileResponse:
    """Get company profile"""
    success, company, message = await CompanyProfileService.get_company_profile(company_id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )
    
    return CompanyProfileResponse.model_validate(company, from_attributes=True)


@router.put("/profile")
async def update_profile(
    request: CompanyProfileUpdateRequest,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
) -> CompanyProfileResponse:
    """Update company profile (name and website)"""
    success, company, message = await CompanyProfileService.update_company_profile(
        company_id,
        request.company_name,
        request.website_url,
        db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return CompanyProfileResponse.model_validate(company, from_attributes=True)


@router.post("/profile/image")
async def upload_profile_image(
    file: UploadFile = File(...),
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
) -> CompanyProfileImageResponse:
    """Upload company profile image"""
    file_content = await file.read()
    
    success, s3_url, message = await CompanyProfileService.upload_profile_image(
        company_id,
        file_content,
        file.filename,
        db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Get updated company to return profile_image_key
    _, company, _ = await CompanyProfileService.get_company_profile(company_id, db)
    
    return CompanyProfileImageResponse(
        message=message,
        s3_url=s3_url,
        profile_image_key=company.profile_image_key
    )
