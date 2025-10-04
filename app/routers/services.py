from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.models.content import Service
from app.core.auth0_security import require_auth0_admin as require_admin
from app.core.security import log_admin_action
from app.core.database import get_supabase
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[Service])
async def get_services():
    """Get all services (public endpoint)

    Tolerant to older database schemas missing generated is_active or order column.
    """
    try:
        supabase = get_supabase()
        # Preferred query path
        try:
            result = (
                supabase
                .table("services")
                .select("*")
                .eq("is_active", True)
                .order("order")
                .execute()
            )
        except Exception:
            # Retry without is_active/order assumptions
            try:
                result = (
                    supabase
                    .table("services")
                    .select("*")
                    .eq("active", True)
                    .execute()
                )
            except Exception:
                result = supabase.table("services").select("*").execute()

        data = result.data or []
        # Python-side stable sort if order key present
        data.sort(key=lambda x: x.get("order", 0))
        return data

    except Exception as e:
        logger.error(f"Get services error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve services"
        )

@router.post("/", response_model=Service)
async def create_service(
    request: Request,
    service: Service,
    current_user: dict = Depends(require_admin)
):
    """Create new service (admin only)"""
    try:
        supabase = get_supabase()
        
        service_data = {
            "title": service.title,
            "description": service.description,
            "icon": service.icon,
            "features": service.features,
            "price": service.price,
            "order": service.order,
            "active": service.active
        }
        
        result = supabase.table("services").insert(service_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create service"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "create_service",
            {"service_title": service.title}
        )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create service"
        )

@router.put("/{service_id}", response_model=Service)
async def update_service(
    service_id: str,
    request: Request,
    service: Service,
    current_user: dict = Depends(require_admin)
):
    """Update service (admin only)"""
    try:
        supabase = get_supabase()
        
        service_data = {
            "title": service.title,
            "description": service.description,
            "icon": service.icon,
            "features": service.features,
            "price": service.price,
            "order": service.order,
            "active": service.active
        }
        
        result = supabase.table("services").update(service_data).eq("id", service_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "update_service",
            {"service_id": service_id, "service_title": service.title}
        )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update service"
        )

@router.delete("/{service_id}")
async def delete_service(
    service_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Delete service (admin only)"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("services").delete().eq("id", service_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "delete_service",
            {"service_id": service_id}
        )
        
        return {"success": True, "message": "Service deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete service"
        )
