from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.models.content import ContactMessage, ContactResponse
from app.core.security import require_admin, log_admin_action
from app.core.database import get_supabase, execute_query
from app.core.config import settings  # Fix: required for REST fallback settings usage
from typing import List, Optional
import os, json, datetime
from app.services.email import send_resend_email, render_contact_email
import httpx
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
# Separate router for admin-compat endpoints mounted at /api (used by admin dashboard)
admin_compat_router = APIRouter()

# Mirror admin endpoints under the main router too, so clients using /contact/messages work in both apps
@router.get("/messages")
async def get_contact_messages_main(
    request: Request,
    current_user: dict = Depends(require_admin),
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False
):
    try:
        return await get_contact_messages(request, current_user, limit, offset, unread_only)  # type: ignore
    except Exception as e:
        logger.error(f"get_contact_messages_main error: {e}")
        raise

@router.patch("/messages/{message_id}/read")
async def mark_message_read_main(
    message_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    try:
        return await mark_message_read(message_id, request, current_user)  # type: ignore
    except Exception as e:
        logger.error(f"mark_message_read_main error: {e}")
        raise

@router.delete("/messages/{message_id}")
async def delete_contact_message_main(
    message_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    try:
        return await delete_contact_message(message_id, request, current_user)  # type: ignore
    except Exception as e:
        logger.error(f"delete_contact_message_main error: {e}")
        raise

@router.post("/", response_model=ContactResponse)
async def submit_contact_form(request: Request, contact: ContactMessage):
    """Submit contact form (public endpoint)
    Resilient behavior: attempts DB insert and email independently.
    Returns success if at least one path succeeds to avoid user-facing failures.
    """
    # Capture client IP (best-effort)
    try:
        contact.ip_address = request.client.host  # type: ignore[attr-defined]
    except Exception:
        pass

    saved = False
    emailed = False

    # 1) Try to save to database (non-fatal on failure)
    try:
        supabase = get_supabase()
        result = supabase.table("contacts").insert({
            "name": contact.name,
            "email": contact.email,
            "subject": contact.subject or "General Inquiry",  # Provide default if no subject
            "message": contact.message,
            "status": "unread",
            "ip_address": contact.ip_address,
        }).execute()
        saved = bool(result.data)
        if not saved:
            logger.error("Contact save returned empty result.data")
    except Exception as e:
        logger.error(f"Contact save failed (non-fatal): {e}")

    # 1b) Fallback: use Supabase REST API directly if not saved
    if not saved:
        try:
            base = settings.SUPABASE_URL.rstrip('/')
            url = f"{base}/rest/v1/contacts"
            headers = {
                "apikey": settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            }
            payload = {
                "name": contact.name,
                "email": contact.email,
                "subject": contact.subject or "General Inquiry",
                "message": contact.message,
                "status": "unread",
                "ip_address": contact.ip_address,
            }
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code in (200, 201):
                    saved = True
                else:
                    logger.error(f"Supabase REST insert failed [{resp.status_code}]: {resp.text}")
        except Exception as e:
            logger.error(f"Supabase REST fallback failed: {e}")

    # 2) Try to send email notification (non-fatal on failure)
    try:
        html = render_contact_email(contact.name, contact.email, contact.message)
        emailed = await send_resend_email(
            subject="New contact message on CortejTech",
            html=html,
        )
        if not emailed:
            logger.error("Contact email send returned False")
    except Exception as e:
        logger.exception(f"Contact email notification failed (non-fatal): {e}")

    # 3) If both failed, persist to a local fallback file (best-effort) and still return success to user
    if not (saved or emailed):
        logger.error("Contact submission failed: neither DB save nor email succeeded; writing to local fallback queue")
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            path = os.path.join(base_dir, "fallback_contacts.jsonl")
            record = {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "ip": getattr(contact, "ip_address", None),
                "name": contact.name,
                "email": contact.email,
                "message": contact.message,
            }
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write contact fallback record: {e}")

    return ContactResponse(
        success=True,
        message="Thank you for your message. We'll get back to you soon!"
    )

# Alias without trailing slash so clients posting to /api/contact (no slash)
# don't hit a 405 due to strict slash handling on POST.
@router.post("", response_model=ContactResponse)
async def submit_contact_form_no_slash(request: Request, contact: ContactMessage):
    return await submit_contact_form(request, contact)

@router.get("/messages", response_model=List[ContactMessage])
async def get_contact_messages(
    request: Request,
    current_user: dict = Depends(require_admin),
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False
):
    """Get contact messages (admin only)"""
    try:
        supabase = get_supabase()
        query = supabase.table("contacts").select("*")
        
        if unread_only:
            query = query.eq("status", "unread")
            
        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        # Transform data to match admin panel expectations
        transformed_data = []
        for message in result.data:
            transformed_message = {
                **message,
                "is_read": message.get("status") == "read",  # Convert status to is_read boolean
                "subject": message.get("subject") or "General Inquiry"  # Ensure subject exists
            }
            transformed_data.append(transformed_message)
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "view_contact_messages",
            {"count": len(transformed_data), "unread_only": unread_only}
        )
        
        return transformed_data
        
    except Exception as e:
        logger.error(f"Get contact messages error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contact messages"
        )

@router.patch("/messages/{message_id}/read")
async def mark_message_read(
    message_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Mark contact message as read (admin only)"""
    try:
        supabase = get_supabase()
        result = supabase.table("contacts").update({
            "status": "read",
        }).eq("id", message_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "mark_message_read",
            {"message_id": message_id}
        )
        
        return {"success": True, "message": "Message marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mark message read error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update message"
        )

@router.delete("/messages/{message_id}")
async def delete_contact_message(
    message_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Delete contact message (admin only)"""
    try:
        supabase = get_supabase()
        result = supabase.table("contacts").delete().eq("id", message_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "delete_contact_message",
            {"message_id": message_id}
        )
        
        return {"success": True, "message": "Message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete contact message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message"
        )

# Admin dashboard compatibility endpoints (mounted at /api -> /api/contacts)
@admin_compat_router.get("/contacts")
async def admin_list_contacts(
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """GET /api/contacts -> list contacts (admin only)"""
    try:
        supabase = get_supabase()
        result = supabase.table("contacts").select("*").order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Admin list contacts error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch contacts")

@admin_compat_router.patch("/contacts")
async def admin_update_contact(
    request: Request,
    payload: dict,
    current_user: dict = Depends(require_admin)
):
    """PATCH /api/contacts -> update contact (admin only)"""
    try:
        supabase = get_supabase()
        contact_id = payload.get("id")
        if not contact_id:
            raise HTTPException(status_code=400, detail="Contact ID is required")
        update_data = {}
        if payload.get("status"):
            update_data["status"] = payload["status"]
        if "response_notes" in payload:
            update_data["response_notes"] = payload.get("response_notes")
        if payload.get("status") == "read":
            update_data["responded_at"] = "now()"
        result = supabase.table("contacts").update(update_data).eq("id", contact_id).select("*").execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Contact not found")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin update contact error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update contact")

@admin_compat_router.delete("/contacts")
async def admin_delete_contact(
    request: Request,
    id: str,
    current_user: dict = Depends(require_admin)
):
    """DELETE /api/contacts?id=... (admin only)"""
    try:
        supabase = get_supabase()
        supabase.table("contacts").delete().eq("id", id).execute()
        return {"success": True}
    except Exception as e:
        logger.error(f"Admin delete contact error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete contact")