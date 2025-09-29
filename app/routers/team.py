from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.models.content import TeamMember
from app.core.security import require_admin, log_admin_action
from app.core.database import get_supabase
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[TeamMember])
async def get_team_members():
    """Get all team members (public endpoint) with schema tolerance"""
    try:
        supabase = get_supabase()
        try:
            result = (
                supabase
                .table("team_members")
                .select("*")
                .eq("active", True)
                .order("order")
                .execute()
            )
        except Exception:
            result = supabase.table("team_members").select("*").execute()

        data = result.data or []
        data.sort(key=lambda x: x.get("order", 0))
        return data

    except Exception as e:
        logger.error(f"Get team members error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve team members"
        )

@router.post("/", response_model=TeamMember)
async def create_team_member(
    request: Request,
    member: TeamMember,
    current_user: dict = Depends(require_admin)
):
    """Create new team member (admin only)"""
    try:
        supabase = get_supabase()
        
        member_data = {
            "name": member.name,
            "position": member.position,
            "bio": member.bio,
            "image": member.image,
            "social_links": member.social_links,
            "order": member.order,
            "active": member.active
        }
        
        result = supabase.table("team_members").insert(member_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create team member"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "create_team_member",
            {"member_name": member.name, "position": member.position}
        )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create team member error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create team member"
        )

@router.put("/{member_id}", response_model=TeamMember)
async def update_team_member(
    member_id: str,
    request: Request,
    member: TeamMember,
    current_user: dict = Depends(require_admin)
):
    """Update team member (admin only)"""
    try:
        supabase = get_supabase()
        
        member_data = {
            "name": member.name,
            "position": member.position,
            "bio": member.bio,
            "image": member.image,
            "social_links": member.social_links,
            "order": member.order,
            "active": member.active
        }
        
        result = supabase.table("team_members").update(member_data).eq("id", member_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "update_team_member",
            {"member_id": member_id, "member_name": member.name}
        )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update team member error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update team member"
        )

@router.delete("/{member_id}")
async def delete_team_member(
    member_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Delete team member (admin only)"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("team_members").delete().eq("id", member_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "delete_team_member",
            {"member_id": member_id}
        )
        
        return {"success": True, "message": "Team member deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete team member error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete team member"
        )