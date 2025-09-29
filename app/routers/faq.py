from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.models.content import FAQ
from app.core.security import require_admin, log_admin_action
from app.core.database import get_supabase
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Default FAQs (maintaining compatibility with existing system)
DEFAULT_FAQS = [
    {
        "id": "default-1",
        "question": "How long does a typical project take?",
        "answer": "Project timelines vary based on complexity. Simple websites take 2-4 weeks, while complex applications can take 2-6 months. We provide detailed timelines during our initial consultation.",
        "category": "general",
        "order": 1,
        "active": True
    },
    {
        "id": "default-2",
        "question": "What technologies do you use?",
        "answer": "We use modern technologies including React, Next.js, Node.js, TypeScript, and cloud platforms like AWS and Vercel to build scalable, high-performance applications.",
        "category": "technical",
        "order": 2,
        "active": True
    },
    {
        "id": "default-3",
        "question": "Do you provide ongoing support?",
        "answer": "Yes! We offer comprehensive maintenance and support packages to keep your digital solutions running smoothly and up-to-date.",
        "category": "support",
        "order": 3,
        "active": True
    },
    {
        "id": "default-4",
        "question": "How do you handle project pricing?",
        "answer": "We provide transparent, fixed-price quotes based on your specific requirements. Contact us for a free consultation and detailed proposal.",
        "category": "pricing",
        "order": 4,
        "active": True
    }
]

@router.get("/", response_model=List[FAQ])
async def get_faqs():
    """Get all FAQs (public endpoint)"""
    try:
        supabase = get_supabase()
        
        try:
            result = supabase.table("faqs").select("*").eq("is_active", True).order("order").execute()
            
            if result.data:
                return result.data
            else:
                # Return default FAQs if none exist in database
                return DEFAULT_FAQS
                
        except Exception:
            # If FAQ table doesn't exist, return default FAQs
            return DEFAULT_FAQS
        
    except Exception as e:
        logger.error(f"Get FAQs error: {e}")
        # Return default FAQs on any error
        return DEFAULT_FAQS

@router.post("/", response_model=FAQ)
async def create_faq(
    request: Request,
    faq: FAQ,
    current_user: dict = Depends(require_admin)
):
    """Create new FAQ (admin only)"""
    try:
        supabase = get_supabase()
        
        faq_data = {
            "question": faq.question,
            "answer": faq.answer,
            "category": faq.category,
            "order": faq.order,
            "active": faq.active
        }
        
        result = supabase.table("faqs").insert(faq_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create FAQ"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "create_faq",
            {"question": faq.question[:50] + "..." if len(faq.question) > 50 else faq.question}
        )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create FAQ error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create FAQ"
        )

@router.put("/{faq_id}", response_model=FAQ)
async def update_faq(
    faq_id: str,
    request: Request,
    faq: FAQ,
    current_user: dict = Depends(require_admin)
):
    """Update FAQ (admin only)"""
    try:
        supabase = get_supabase()
        
        faq_data = {
            "question": faq.question,
            "answer": faq.answer,
            "category": faq.category,
            "order": faq.order,
            "active": faq.active
        }
        
        result = supabase.table("faqs").update(faq_data).eq("id", faq_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FAQ not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "update_faq",
            {"faq_id": faq_id, "question": faq.question[:50] + "..." if len(faq.question) > 50 else faq.question}
        )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update FAQ error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update FAQ"
        )

@router.delete("/{faq_id}")
async def delete_faq(
    faq_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """Delete FAQ (admin only)"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("faqs").delete().eq("id", faq_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FAQ not found"
            )
        
        # Log admin action
        await log_admin_action(
            request,
            current_user["email"],
            "delete_faq",
            {"faq_id": faq_id}
        )
        
        return {"success": True, "message": "FAQ deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete FAQ error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete FAQ"
        )