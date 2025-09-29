from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.models.content import AboutContent
from app.core.security import require_admin, log_admin_action
from app.core.database import get_supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/about")
async def get_about_content():
    """Get about page content (public endpoint)"""
    try:
        supabase = get_supabase()
        # In provided schema, about has fields: content, created_at, updated_at
        result = (
            supabase
            .table("about")
            .select("*")
            .order("updated_at", desc=True)
            .limit(1)
            .execute()
        )

        if result.data:
            return {"success": True, "about": result.data[0]}
        else:
            # Default/fallback content
            return {
                "success": True,
                "about": {
                    "content": (
                        "We are a technology company focused on delivering innovative solutions."
                    ),
                    "mission": "To provide cutting-edge technology solutions that drive business growth.",
                    "vision": "To be the leading technology partner for businesses worldwide.",
                    "values": ["Innovation", "Quality", "Customer Focus", "Integrity"],
                },
            }

    except Exception as e:
        logger.error(f"Get about content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve about content",
        )

@router.put("/about")
async def update_about_content(
    request: Request, about: AboutContent, current_user: dict = Depends(require_admin)
):
    """Update about page content (admin only)"""
    try:
        supabase = get_supabase()

        # Check if content exists
        existing = supabase.table("about").select("id").limit(1).execute()

        about_data = {
            # schema has only content; keep extra fields if present
            "content": about.content,
            "updated_at": "now()",
        }

        if existing.data:
            result = (
                supabase.table("about").update(about_data).eq("id", existing.data[0]["id"]).execute()
            )
        else:
            result = supabase.table("about").insert(about_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update about content",
            )

        # Log admin action
        await log_admin_action(
            request, current_user["email"], "update_about_content", {"content_len": len(about.content)}
        )

        return {"success": True, "about": result.data[0]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update about content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update about content",
        )

# ===== Public content endpoints to mirror Next.js routes =====

@router.get("/services")
async def public_services():
    """GET /api/content/services -> { services: [...] }"""
    try:
        supabase = get_supabase()
        result = (
            supabase
            .table("services")
            .select("*")
            .eq("is_active", True)
            .order("created_at", desc=True)
            .execute()
        )
        return {"services": result.data or []}
    except Exception as e:
        logger.error(f"Public services error: {e}")
        return {"services": []}

@router.get("/team")
async def public_team():
    """GET /api/content/team -> { team: [...] }"""
    try:
        supabase = get_supabase()
        result = (
            supabase
            .table("team")
            .select("*")
            .eq("is_active", True)
            .order("created_at", desc=True)
            .execute()
        )
        return {"team": result.data or []}
    except Exception as e:
        logger.error(f"Public team error: {e}")
        return {"team": []}

@router.get("/portfolio")
async def public_portfolio():
    """GET /api/content/portfolio -> { portfolio: [...] }"""
    try:
        supabase = get_supabase()
        # Fetch recent rows and filter in Python to allow both is_active and active flags
        result = (
            supabase
            .table("portfolio")
            .select("*")
            .order("display_order", desc=False)
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )

        rows = result.data or []
        items = []
        for row in rows:
            # Determine inclusion using flexible active flags logic:
            # - If either is_active or active is True -> include
            # - If both are present and neither is True -> exclude
            # - If neither field exists -> include (assume visible)
            has_is = "is_active" in row
            has_active = "active" in row
            if has_is or has_active:
                is_true = (row.get("is_active") is True) or (row.get("active") is True)
                if not is_true:
                    continue
            # Status: exclude drafts/archived/deleted if provided
            status = (row.get("status") or "").lower()
            if status in {"draft", "archived", "deleted"}:
                continue
            items.append(row)

        return {"portfolio": items}
    except Exception as e:
        logger.error(f"Public portfolio error: {e}")
        return {"portfolio": []}

@router.get("/faq")
async def public_faq():
    """GET /api/content/faq -> { faqs: [...] }"""
    try:
        supabase = get_supabase()
        result = (
            supabase
            .table("faqs")
            .select("*")
            .eq("is_active", True)
            .order("sort_order", desc=False)
            .order("updated_at", desc=True)
            .execute()
        )
        return {"faqs": result.data or []}
    except Exception as e:
        logger.error(f"Public FAQ error: {e}")
        return {"faqs": []}

@router.get("/testimonials")
async def public_testimonials():
    """GET /api/content/testimonials -> { testimonials: [...] }"""
    try:
        supabase = get_supabase()
        result = (
            supabase
            .table("testimonials")
            .select("*")
            .eq("is_active", True)
            .order("order", desc=False)
            .execute()
        )
        data = result.data or []
        # Fallback to `active` flag if `is_active` not set
        if not data:
            try:
                result = (
                    supabase
                    .table("testimonials")
                    .select("*")
                    .eq("active", True)
                    .order("order", desc=False)
                    .execute()
                )
                data = result.data or []
            except Exception:
                data = []
        return {"testimonials": data}
    except Exception as e:
        logger.error(f"Public testimonials error: {e}")
        return {"testimonials": []}