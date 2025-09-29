from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.core.security import require_admin, log_admin_action
from app.core.database import get_supabase
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_admin_info():
    """Get admin API information and available endpoints"""
    return {
        "message": "Admin API",
        "endpoints": [
            "GET /dashboard/stats - Get dashboard statistics",
            "GET /contacts - Get all contact messages",
            "PUT /contacts/{contact_id} - Update contact message", 
            "DELETE /contacts/{contact_id} - Delete contact message"
        ]
    }

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Get dashboard statistics (admin only)"""
    try:
        supabase = get_supabase()
        
        # Get various counts
        stats = {}
        
        # Contacts
        try:
            contact_result = supabase.table("contacts").select("id", count="exact").execute()
            stats["total_messages"] = contact_result.count or 0
            unread_result = supabase.table("contacts").select("id", count="exact").eq("status", 'unread').execute()
            stats["unread_messages"] = unread_result.count or 0
        except Exception:
            stats["total_messages"] = 0
            stats["unread_messages"] = 0
        
        # Services
        try:
            services_result = supabase.table("services").select("id", count="exact").execute()
            stats["total_services"] = services_result.count or 0
        except Exception:
            stats["total_services"] = 0
        
        # Team members
        try:
            team_result = supabase.table("team_members").select("id", count="exact").execute()
            stats["total_team_members"] = team_result.count or 0
        except Exception:
            stats["total_team_members"] = 0
        
        # Portfolio projects
        try:
            portfolio_result = supabase.table("portfolio").select("id", count="exact").execute()
            stats["total_portfolio_projects"] = portfolio_result.count or 0
        except Exception:
            stats["total_portfolio_projects"] = 0
        
        # Testimonials
        try:
            testimonials_result = supabase.table("testimonials").select("id", count="exact").execute()
            stats["total_testimonials"] = testimonials_result.count or 0
        except Exception:
            stats["total_testimonials"] = 0
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "view_dashboard_stats",
            stats
        )
        
        return {"success": True, "stats": stats}
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )

@router.get("/audit-log")
async def get_audit_log(
    request: Request,
    current_user: dict = Depends(require_admin),
    limit: int = 100,
    offset: int = 0
):
    """Get admin audit log (admin only)"""
    try:
        supabase = get_supabase()
        result = supabase.table("admin_audit_logs").select("*").order("timestamp", desc=True).range(offset, offset + limit - 1).execute()

        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "view_audit_log",
            {"count": len(result.data)}
        )

        return {"success": True, "logs": result.data}
        
    except Exception as e:
        logger.error(f"Audit log error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit log"
        )

@router.get("/users")
async def get_admin_users(
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Get admin users list (admin only)"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("app_admins").select("id, email, created_at, last_login, is_active").execute()
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "view_admin_users",
            {"count": len(result.data)}
        )
        
        return {"success": True, "users": result.data}
        
    except Exception as e:
        logger.error(f"Get admin users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin users"
        )

@router.post("/users")
async def create_admin_user(
    request: Request,
    user_data: Dict[str, Any],
    current_user: dict = Depends(require_admin)
):
    """Create new admin user (admin only)"""
    try:
        email = user_data.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        supabase = get_supabase()
        
        result = supabase.table("app_admins").insert({
            "email": email,
            "is_active": user_data.get("is_active", True)
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create admin user"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "create_admin_user",
            {"new_user_email": email}
        )
        
        return {"success": True, "user": result.data[0]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create admin user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create admin user"
        )

@router.delete("/users/{user_id}")
async def delete_admin_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Delete admin user (admin only)"""
    try:
        supabase = get_supabase()

        # Get user info before deletion
        user_result = supabase.table("app_admins").select("email").eq("id", user_id).execute()
        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        deleted_email = user_result.data[0]["email"]

        # Don't allow deleting yourself
        if deleted_email == current_user["email"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own admin account"
            )

        # Perform deletion
        supabase.table("app_admins").delete().eq("id", user_id).execute()

        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "delete_admin_user",
            {"deleted_user_email": deleted_email}
        )

        return {"success": True, "message": "Admin user deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete admin user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete admin user"
        )