from fastapi import APIRouter, Depends, UploadFile, File, Query, Form
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.modules.auth.routes import get_current_company
from app.modules.newsletters.newsletter_templates.schemas import (
    TemplateCreateRequest,
    TemplateUpdateRequest,
)
from app.modules.newsletters.newsletter_templates.handlers import TemplateHandler, AssetHandler


router = APIRouter(prefix="/api/newsletters", tags=["Newsletter Templates"])


@router.post(
    "/templates",
    status_code=201,
    summary="Create newsletter template with assets",
    description="Create a new newsletter template with optional file uploads"
)
async def create_template(
    name: str = Form(..., min_length=1, max_length=100),
    subject: str = Form(..., min_length=1, max_length=255),
    html_content: str = Form(...),
    text_content: Optional[str] = Form(None),
    constants: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    request = TemplateCreateRequest(
        name=name,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        constants=[v.strip() for v in constants.split(",") if v.strip()] if constants else []
    )
    return await TemplateHandler.create_template_with_assets(
        company_id, request, files, db
    )


@router.put(
    "/templates/{template_id}",
    status_code=200,
    summary="Update newsletter template with assets",
    description="Update an existing newsletter template with optional file uploads"
)
async def update_template(
    template_id: str,
    name: Optional[str] = Form(None, max_length=100),
    subject: Optional[str] = Form(None, max_length=255),
    html_content: Optional[str] = Form(None),
    text_content: Optional[str] = Form(None),
    constants: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    request = TemplateUpdateRequest(
        name=name,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        constants=[v.strip() for v in constants.split(",") if v.strip()] if constants and constants.strip() else None,
        is_active=is_active
    )
    return await TemplateHandler.update_template_with_assets(
        company_id, template_id, request, files, db
    )


@router.get(
    "/templates/{template_id}",
    status_code=200,
    summary="Get newsletter template",
    description="Retrieve a specific newsletter template"
)
async def get_template(
    template_id: str,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await TemplateHandler.get_template(company_id, template_id, db)


@router.get(
    "/templates",
    status_code=200,
    summary="List newsletter templates",
    description="List all templates for a company with pagination"
)
async def list_templates(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await TemplateHandler.list_templates(company_id, db, page, limit)


@router.patch(
    "/templates/{template_id}/deactivate",
    status_code=200,
    summary="Deactivate template",
    description="Deactivate a newsletter template"
)
async def deactivate_template(
    template_id: str,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await TemplateHandler.deactivate_template(company_id, template_id, db)


@router.delete(
    "/templates/{template_id}",
    status_code=200,
    summary="Delete template",
    description="Permanently delete a newsletter template"
)
async def delete_template(
    template_id: str,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await TemplateHandler.delete_template(company_id, template_id, db)


@router.get(
    "/templates/{template_id}/versions",
    status_code=200,
    summary="Get template versions",
    description="List all versions of a template"
)
async def get_versions(
    template_id: str,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await TemplateHandler.get_versions(company_id, template_id, db)


@router.get(
    "/templates/{template_id}/versions/{version_id}",
    status_code=200,
    summary="Get specific version",
    description="Retrieve a specific version of a template"
)
async def get_version(
    template_id: str,
    version_id: str,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await TemplateHandler.get_version(company_id, template_id, version_id, db)


@router.post(
    "/templates/{template_id}/assets",
    status_code=201,
    summary="Upload template asset",
    description="Upload an image/asset to a template"
)
async def upload_asset(
    template_id: str,
    file: UploadFile = File(...),
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await AssetHandler.upload_asset(company_id, template_id, file, db)


@router.delete(
    "/templates/assets/{asset_id}",
    status_code=200,
    summary="Delete asset",
    description="Delete an uploaded asset"
)
async def delete_asset(
    asset_id: str,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await AssetHandler.delete_asset(company_id, asset_id, db)


@router.get(
    "/templates/{template_id}/assets",
    status_code=200,
    summary="Get template assets",
    description="List all assets for a template"
)
async def get_assets(
    template_id: str,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    return await AssetHandler.get_assets(company_id, template_id, db)
