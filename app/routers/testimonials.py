from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.models.content import Testimonial
from app.core.auth0_security import require_auth0_admin as require_admin
from app.core.security import log_admin_action
from app.core.database import get_supabase
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[Testimonial])
async def get_testimonials():
    """Get all testimonials (public endpoint) with graceful fallbacks"""
    try:
        supabase = get_supabase()
        try:
            result = (
                supabase
                .table("testimonials")
                .select("*")
                .eq("is_active", True)
                .order("order")
                .execute()
            )
        except Exception:
            try:
                result = (
                    supabase
                    .table("testimonials")
                    .select("*")
                    .eq("active", True)
                    .execute()
                )
            except Exception:
                result = supabase.table("testimonials").select("*").execute()

        data = result.data or []
        data.sort(key=lambda x: x.get("order", 0))
        return data
    except Exception as e:
        logger.error(f"Get testimonials error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve testimonials"
        )

@router.post("/", response_model=Testimonial)
async def create_testimonial(
    request: Request,
    testimonial: Testimonial,
    current_user: dict = Depends(require_admin)
):
    """Create new testimonial (admin only)"""
    try:
        supabase = get_supabase()
        
        testimonial_data = {
            "name": testimonial.name,
            "company": testimonial.company,
            "position": testimonial.position,
            "content": testimonial.content,
            "rating": testimonial.rating,
            "image": testimonial.image,
            "featured": testimonial.featured,
            "order": testimonial.order,
            "active": testimonial.active
        }
        
        result = supabase.table("testimonials").insert(testimonial_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create testimonial"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "create_testimonial",
            {"testimonial_name": testimonial.name, "company": testimonial.company}
        )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create testimonial error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create testimonial"
        )

@router.put("/{testimonial_id}", response_model=Testimonial)
async def update_testimonial(
    testimonial_id: str,
    request: Request,
    testimonial: Testimonial,
    current_user: dict = Depends(require_admin)
):
    """Update testimonial (admin only)"""
    try:
        supabase = get_supabase()
        
        testimonial_data = {
            "name": testimonial.name,
            "company": testimonial.company,
            "position": testimonial.position,
            "content": testimonial.content,
            "rating": testimonial.rating,
            "image": testimonial.image,
            "featured": testimonial.featured,
            "order": testimonial.order,
            "active": testimonial.active
        }
        
        result = supabase.table("testimonials").update(testimonial_data).eq("id", testimonial_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Testimonial not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "update_testimonial",
            {"testimonial_id": testimonial_id, "testimonial_name": testimonial.name}
        )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update testimonial error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update testimonial"
        )

@router.delete("/{testimonial_id}")
async def delete_testimonial(
    testimonial_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Delete testimonial (admin only)"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("testimonials").delete().eq("id", testimonial_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Testimonial not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "delete_testimonial",
            {"testimonial_id": testimonial_id}
        )
        
        return {"success": True, "message": "Testimonial deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete testimonial error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete testimonial"
        )
