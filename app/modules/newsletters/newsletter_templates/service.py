import uuid
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from loguru import logger

from app.modules.auth.model import Company
from app.modules.newsletters.newsletter_templates.model import NewsletterTemplate
from app.modules.newsletters.template_versions.model import NewsletterTemplateVersion
from app.modules.newsletters.template_assets.model import TemplateAsset
from app.modules.campaign.model import Campaign
from app.modules.newsletters.newsletter_templates.schemas import (
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateResponse,
    TemplateListResponse,
    TemplateListItem,
    TemplateVersionResponse,
    TemplateAssetResponse,
)
from app.modules.newsletters.template_assets.service import AssetService


class TemplateService:

    @staticmethod
    async def create_template(
        company_id: str,
        request: TemplateCreateRequest,
        db: Session
    ) -> Tuple[bool, Optional[NewsletterTemplate], str]:
        try:
            # Check if company is on free tier and already has a template
            company = db.query(Company).filter(Company.id == uuid.UUID(company_id)).first()
            if not company:
                return False, None, "Company not found"
            
            if company.subscription_tier == "free":
                # Free tier can only have 1 template
                template_count = db.query(func.count(NewsletterTemplate.id)).filter(
                    NewsletterTemplate.company_id == uuid.UUID(company_id)
                ).scalar() or 0
                
                if template_count >= 1:
                    return False, None, "Free tier limited to 1 template. Upgrade to premium for unlimited templates."
            
            template_id = uuid.uuid4()
            
            new_template = NewsletterTemplate(
                id=template_id,
                company_id=uuid.UUID(company_id),
                name=request.name,
                subject=request.subject,
                html_content=request.html_content,
                text_content=request.text_content,
                constants=request.constants or [],
                is_active=True,
            )
            
            db.add(new_template)
            db.flush()
            
            initial_version = NewsletterTemplateVersion(
                id=uuid.uuid4(),
                template_id=template_id,
                subject=request.subject,
                html_content=request.html_content,
                text_content=request.text_content,
                constants=request.constants or [],
            )
            
            db.add(initial_version)
            db.commit()
            db.refresh(new_template)
            
            logger.info(f"Template created: {template_id} for company {company_id}")
            return True, new_template, "Template created successfully"
            
        except Exception as e:
            db.rollback()
            logger.error(f"Template creation error for company {company_id}: {str(e)}")
            return False, None, "Failed to create template"

    @staticmethod
    async def update_template(
        company_id: str,
        template_id: str,
        request: TemplateUpdateRequest,
        db: Session
    ) -> Tuple[bool, Optional[NewsletterTemplate], str]:
        try:
            template = db.query(NewsletterTemplate).filter(
                NewsletterTemplate.id == uuid.UUID(template_id),
                NewsletterTemplate.company_id == uuid.UUID(company_id)
            ).first()
            
            if not template:
                return False, None, "Template not found"
            
            old_subject = template.subject
            old_html = template.html_content
            old_text = template.text_content
            old_constants = template.constants
            
            content_changed = False
            
            if request.subject and request.subject != old_subject:
                template.subject = request.subject
                content_changed = True
            
            if request.html_content and request.html_content != old_html:
                template.html_content = request.html_content
                content_changed = True
            
            if request.text_content and request.text_content != old_text:
                template.text_content = request.text_content
                content_changed = True
            
            if request.constants and request.constants != old_constants:
                template.constants = request.constants
                content_changed = True
            
            if request.name:
                template.name = request.name
            
            if request.is_active is not None:
                template.is_active = request.is_active
            
            if content_changed:
                # Check free tier version limit
                company = db.query(Company).filter(Company.id == uuid.UUID(company_id)).first()
                if company and company.subscription_tier == "free":
                    version_count = db.query(NewsletterTemplateVersion).filter(
                        NewsletterTemplateVersion.template_id == uuid.UUID(template_id)
                    ).count()
                    
                    if version_count >= 3:  # Free tier limit: 3 versions
                        logger.warning(f"Free tier version limit exceeded for company {company_id}")
                        return False, None, "Free tier limited to 3 versions per template"
                
                new_version = NewsletterTemplateVersion(
                    id=uuid.uuid4(),
                    template_id=uuid.UUID(template_id),
                    subject=template.subject,
                    html_content=template.html_content,
                    text_content=template.text_content,
                    constants=template.constants,
                )
                db.add(new_version)
            
            template.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(template)
            
            logger.info(f"Template updated: {template_id}, content_changed: {content_changed}")
            return True, template, "Template updated successfully"
            
        except Exception as e:
            db.rollback()
            logger.error(f"Template update error for {template_id}: {str(e)}")
            return False, None, "Failed to update template"

    @staticmethod
    async def get_template(
        company_id: str,
        template_id: str,
        db: Session
    ) -> Optional[NewsletterTemplate]:
        try:
            template = db.query(NewsletterTemplate).filter(
                NewsletterTemplate.id == uuid.UUID(template_id),
                NewsletterTemplate.company_id == uuid.UUID(company_id)
            ).first()
            return template
        except Exception as e:
            logger.error(f"Get template error for {template_id}: {str(e)}")
            return None

    @staticmethod
    async def list_templates(
        company_id: str,
        db: Session,
        page: int = 1,
        limit: int = 20
    ) -> TemplateListResponse:
        try:
            skip = (page - 1) * limit
            
            total = db.query(func.count(NewsletterTemplate.id)).filter(
                NewsletterTemplate.company_id == uuid.UUID(company_id)
            ).scalar() or 0
            
            templates = db.query(NewsletterTemplate).filter(
                NewsletterTemplate.company_id == uuid.UUID(company_id)
            ).order_by(desc(NewsletterTemplate.updated_at)).offset(skip).limit(limit).all()
            
            items = [
                TemplateListItem(
                    id=t.id,
                    name=t.name,
                    subject=t.subject,
                    constants=t.constants or [],
                    is_active=t.is_active,
                    updated_at=t.updated_at
                )
                for t in templates
            ]
            
            return TemplateListResponse(
                items=items,
                total=total,
                page=page,
                limit=limit
            )
        except Exception as e:
            logger.error(f"List templates error for company {company_id}: {str(e)}")
            return TemplateListResponse(items=[], total=0, page=page, limit=limit)

    @staticmethod
    async def deactivate_template(
        company_id: str,
        template_id: str,
        db: Session
    ) -> Tuple[bool, str]:
        try:
            template = db.query(NewsletterTemplate).filter(
                NewsletterTemplate.id == uuid.UUID(template_id),
                NewsletterTemplate.company_id == uuid.UUID(company_id)
            ).first()
            
            if not template:
                return False, "Template not found"
            
            template.is_active = False
            template.updated_at = datetime.now(timezone.utc)
            db.commit()
            
            logger.info(f"Template deactivated: {template_id}")
            return True, "Template deactivated successfully"
            
        except Exception as e:
            db.rollback()
            logger.error(f"Deactivate template error for {template_id}: {str(e)}")
            return False, "Failed to deactivate template"

    @staticmethod
    async def delete_template(
        company_id: str,
        template_id: str,
        db: Session
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Delete a template and cascade delete any campaigns using it.
        Returns: (success, message, affected_campaigns)
        """
        try:
            template = db.query(NewsletterTemplate).filter(
                NewsletterTemplate.id == uuid.UUID(template_id),
                NewsletterTemplate.company_id == uuid.UUID(company_id)
            ).first()
            
            if not template:
                return False, "Template not found", []
            
            # Get all campaigns using this template (will be cascade deleted)
            affected_campaigns = db.query(Campaign).filter(
                Campaign.template_id == uuid.UUID(template_id),
                Campaign.company_id == uuid.UUID(company_id)
            ).all()
            
            affected_campaign_data = [
                {
                    "id": str(camp.id),
                    "name": camp.name,
                    "status": camp.status,
                    "scheduled_for": camp.scheduled_for.isoformat() if camp.scheduled_for else None
                }
                for camp in affected_campaigns
            ]
            
            db.delete(template)
            db.commit()
            
            logger.info(
                f"Template deleted: {template_id}, "
                f"affected campaigns: {len(affected_campaigns)}"
            )
            return True, "Template deleted successfully", affected_campaign_data
            
        except Exception as e:
            db.rollback()
            logger.error(f"Delete template error for {template_id}: {str(e)}")
            return False, "Failed to delete template", []

    @staticmethod
    async def get_template_versions(
        company_id: str,
        template_id: str,
        db: Session
    ) -> List[TemplateVersionResponse]:
        try:
            template = db.query(NewsletterTemplate).filter(
                NewsletterTemplate.id == uuid.UUID(template_id),
                NewsletterTemplate.company_id == uuid.UUID(company_id)
            ).first()
            
            if not template:
                return []
            
            versions = db.query(NewsletterTemplateVersion).filter(
                NewsletterTemplateVersion.template_id == uuid.UUID(template_id)
            ).order_by(desc(NewsletterTemplateVersion.created_at)).all()
            
            return [
                TemplateVersionResponse(
                    id=v.id,
                    template_id=v.template_id,
                    subject=v.subject,
                    html_content=v.html_content,
                    text_content=v.text_content,
                    variables=v.variables,
                    created_at=v.created_at
                )
                for v in versions
            ]
        except Exception as e:
            logger.error(f"Get versions error for {template_id}: {str(e)}")
            return []

    @staticmethod
    async def get_version(
        company_id: str,
        template_id: str,
        version_id: str,
        db: Session
    ) -> Optional[TemplateVersionResponse]:
        try:
            template = db.query(NewsletterTemplate).filter(
                NewsletterTemplate.id == uuid.UUID(template_id),
                NewsletterTemplate.company_id == uuid.UUID(company_id)
            ).first()
            
            if not template:
                return None
            
            version = db.query(NewsletterTemplateVersion).filter(
                NewsletterTemplateVersion.id == uuid.UUID(version_id),
                NewsletterTemplateVersion.template_id == uuid.UUID(template_id)
            ).first()
            
            if not version:
                return None
            
            return TemplateVersionResponse(
                id=version.id,
                template_id=version.template_id,
                subject=version.subject,
                html_content=version.html_content,
                text_content=version.text_content,
                variables=version.variables,
                created_at=version.created_at
            )
        except Exception as e:
            logger.error(f"Get version error for {version_id}: {str(e)}")
            return None
