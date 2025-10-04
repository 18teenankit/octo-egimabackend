from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.models.content import Portfolio
from app.core.auth0_security import require_auth0_admin as require_admin
from app.core.security import log_admin_action
from app.core.database import get_supabase
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[Portfolio])
async def get_portfolio_projects():
    """Get all portfolio projects (public endpoint) with schema tolerance"""
    try:
        supabase = get_supabase()
        try:
            result = (
                supabase
                .table("portfolio")
                .select("*")
                .eq("is_active", True)
                .order("display_order")
                .execute()
            )
        except Exception:
            try:
                result = (
                    supabase
                    .table("portfolio")
                    .select("*")
                    .eq("active", True)
                    .execute()
                )
            except Exception:
                result = supabase.table("portfolio").select("*").execute()

        data = result.data or []
        data.sort(key=lambda x: x.get("display_order", 0))
        return data
    except Exception as e:
        logger.error(f"Get portfolio projects error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve portfolio projects"
        )

@router.post("/", response_model=Portfolio)
async def create_portfolio_project(
    request: Request,
    project: Portfolio,
    current_user: dict = Depends(require_admin)
):
    """Create new portfolio project (admin only)"""
    try:
        supabase = get_supabase()

        project_data = {
            "title": project.title,
            "description": project.description,
            "client_name": project.client_name,
            "category": project.category,
            "technologies": project.technologies,
            "project_url": project.project_url,
            "image_url": project.image_url,
            "image_gallery": project.image_gallery,
            "featured_image": project.featured_image,
            "status": project.status,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "project_duration": project.project_duration,
            "team_size": project.team_size,
            "testimonial_quote": project.testimonial_quote,
            "display_order": project.display_order,
            "is_featured": project.is_featured,
            "is_case_study": project.is_case_study,
            "seo_title": project.seo_title,
            "seo_description": project.seo_description,
            "slug": project.slug,
            "active": project.active
    }

        result = supabase.table("portfolio").insert(project_data).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create portfolio project")
        await log_admin_action(request, current_user["email"], "create_portfolio_project", {"project_title": project.title, "category": project.category})
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create portfolio project error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create portfolio project")

@router.put("/{project_id}", response_model=Portfolio)
async def update_portfolio_project(
    project_id: str,
    request: Request,
    project: Portfolio,
    current_user: dict = Depends(require_admin)
):
    """Update portfolio project (admin only)"""
    try:
        supabase = get_supabase()

        project_data = {
            "title": project.title,
            "description": project.description,
            "client_name": project.client_name,
            "category": project.category,
            "technologies": project.technologies,
            "project_url": project.project_url,
            "image_url": project.image_url,
            "image_gallery": project.image_gallery,
            "featured_image": project.featured_image,
            "status": project.status,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "project_duration": project.project_duration,
            "team_size": project.team_size,
            "testimonial_quote": project.testimonial_quote,
            "display_order": project.display_order,
            "is_featured": project.is_featured,
            "is_case_study": project.is_case_study,
            "seo_title": project.seo_title,
            "seo_description": project.seo_description,
            "slug": project.slug,
            "active": project.active
    }

        result = supabase.table("portfolio").update(project_data).eq("id", project_id).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio project not found")
        await log_admin_action(request, current_user["email"], "update_portfolio_project", {"project_id": project_id, "project_title": project.title})
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update portfolio project error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update portfolio project")

@router.delete("/{project_id}")
async def delete_portfolio_project(
    project_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Delete portfolio project (admin only)"""
    try:
        supabase = get_supabase()

        result = supabase.table("portfolio").delete().eq("id", project_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio project not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "delete_portfolio_project",
            {"project_id": project_id}
        )
        
        return {"success": True, "message": "Portfolio project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete portfolio project error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete portfolio project"
        )
