from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class ContactMessage(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    subject: Optional[str] = None
    message: str
    created_at: Optional[datetime] = None
    is_read: bool = False
    ip_address: Optional[str] = None

class ContactResponse(BaseModel):
    success: bool
    message: str

class Service(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    icon: Optional[str] = None
    features: List[str] = []
    price: Optional[str] = None
    order: int = 0
    active: bool = True

class TeamMember(BaseModel):
    id: Optional[str] = None
    name: str
    position: str
    bio: Optional[str] = None
    image: Optional[str] = None
    social_links: Dict[str, str] = {}
    order: int = 0
    active: bool = True

class Portfolio(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    client_name: Optional[str] = None
    category: Optional[str] = None
    technologies: Optional[List[str]] = []
    project_url: Optional[str] = None
    image_url: Optional[str] = None
    image_gallery: Optional[List[str]] = []
    featured_image: Optional[str] = None
    status: str = "completed"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    project_duration: Optional[str] = None
    team_size: Optional[int] = None
    testimonial_quote: Optional[str] = None
    display_order: int = 0
    is_featured: bool = False
    is_case_study: bool = False
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    slug: Optional[str] = None
    active: bool = True

class FAQ(BaseModel):
    id: Optional[str] = None
    question: str
    answer: str
    category: Optional[str] = None
    order: int = 0
    active: bool = True

class Testimonial(BaseModel):
    id: Optional[str] = None
    name: str
    company: Optional[str] = None
    position: Optional[str] = None
    content: str
    rating: int = 5
    image: Optional[str] = None
    featured: bool = False
    order: int = 0
    active: bool = True

class AboutContent(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: List[str] = []
    updated_at: Optional[datetime] = None