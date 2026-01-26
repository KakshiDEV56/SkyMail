from typing import Optional, List
from fastapi import HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from loguru import logger

from app.modules.newsletters.newsletter_templates.service import TemplateService
from app.modules.newsletters.template_assets.service import AssetService
from app.modules.newsletters.newsletter_templates.schemas import (
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateResponse,
    TemplateAssetResponse,
)


class TemplateHandler:

    @staticmethod
    async def create_template(
        company_id: str,
        request: TemplateCreateRequest,
        db: Session
    ) -> TemplateResponse:
        success, template, message = await TemplateService.create_template(
            company_id, request, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return TemplateResponse.model_validate(template, from_attributes=True)

    @staticmethod
    async def create_template_with_assets(
        company_id: str,
        request: TemplateCreateRequest,
        files: Optional[List[UploadFile]],
        db: Session
    ) -> TemplateResponse:
        """Create template and upload associated assets"""
        # Create template first
        success, template, message = await TemplateService.create_template(
            company_id, request, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Upload files if provided
        if files:
            try:
                for file in files:
                    file_content = await file.read()
                    await AssetService.upload_asset(
                        company_id=company_id,
                        template_id=str(template.id),
                        file_content=file_content,
                        filename=file.filename,
                        db=db
                    )
                    logger.info(f"Uploaded asset {file.filename} to template {template.id}")
            except Exception as e:
                logger.error(f"Error uploading assets: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error uploading assets: {str(e)}"
                )
        
        # Re-fetch template to populate assets relationship
        template = await TemplateService.get_template(company_id, str(template.id), db)
        return TemplateResponse.model_validate(template, from_attributes=True)

    @staticmethod
    async def update_template(
        company_id: str,
        template_id: str,
        request: TemplateUpdateRequest,
        db: Session
    ) -> TemplateResponse:
        success, template, message = await TemplateService.update_template(
            company_id, template_id, request, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return TemplateResponse.model_validate(template, from_attributes=True)

    @staticmethod
    async def update_template_with_assets(
        company_id: str,
        template_id: str,
        request: TemplateUpdateRequest,
        files: Optional[List[UploadFile]],
        db: Session
    ) -> TemplateResponse:
        """Update template and upload associated assets"""
        # Update template first
        success, template, message = await TemplateService.update_template(
            company_id, template_id, request, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Upload files if provided
        if files:
            try:
                for file in files:
                    file_content = await file.read()
                    await AssetService.upload_asset(
                        company_id=company_id,
                        template_id=str(template.id),
                        file_content=file_content,
                        filename=file.filename,
                        db=db
                    )
                    logger.info(f"Uploaded asset {file.filename} to template {template.id}")
            except Exception as e:
                logger.error(f"Error uploading assets: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error uploading assets: {str(e)}"
                )
        
        # Re-fetch template to populate assets relationship
        template = await TemplateService.get_template(company_id, str(template.id), db)
        return TemplateResponse.model_validate(template, from_attributes=True)

    @staticmethod
    async def get_template(
        company_id: str,
        template_id: str,
        db: Session
    ) -> TemplateResponse:
        template = await TemplateService.get_template(company_id, template_id, db)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return TemplateResponse.model_validate(template, from_attributes=True)

    @staticmethod
    async def list_templates(
        company_id: str,
        db: Session,
        page: int = 1,
        limit: int = 20
    ):
        return await TemplateService.list_templates(company_id, db, page, limit)

    @staticmethod
    async def deactivate_template(
        company_id: str,
        template_id: str,
        db: Session
    ):
        success, message = await TemplateService.deactivate_template(
            company_id, template_id, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        
        return {"message": message}

    @staticmethod
    async def delete_template(
        company_id: str,
        template_id: str,
        db: Session
    ):
        success, message, affected_campaigns = await TemplateService.delete_template(
            company_id, template_id, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        
        return {
            "message": message,
            "affected_campaigns": affected_campaigns,
            "deleted_campaigns_count": len(affected_campaigns)
        }

    @staticmethod
    async def get_versions(
        company_id: str,
        template_id: str,
        db: Session
    ):
        versions = await TemplateService.get_template_versions(
            company_id, template_id, db
        )
        
        if not versions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No versions found"
            )
        
        return {"versions": versions}

    @staticmethod
    async def get_version(
        company_id: str,
        template_id: str,
        version_id: str,
        db: Session
    ):
        version = await TemplateService.get_version(
            company_id, template_id, version_id, db
        )
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )
        
        return version


class AssetHandler:

    @staticmethod
    async def upload_asset(
        company_id: str,
        template_id: str,
        file: UploadFile,
        db: Session
    ) -> TemplateAssetResponse:
        file_content = await file.read()
        
        success, asset, message = await AssetService.upload_asset(
            company_id, template_id, file_content, file.filename, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return TemplateAssetResponse.model_validate(asset, from_attributes=True)

    @staticmethod
    async def delete_asset(
        company_id: str,
        asset_id: str,
        db: Session
    ):
        success, message = await AssetService.delete_asset(company_id, asset_id, db)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        
        return {"message": message}

    @staticmethod
    async def get_assets(
        company_id: str,
        template_id: str,
        db: Session
    ):
        assets = await AssetService.get_template_assets(company_id, template_id, db)
        
        return {
            "assets": [
                TemplateAssetResponse.model_validate(asset, from_attributes=True)
                for asset in assets
            ]
        }
