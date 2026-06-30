# schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class StudentUpdateSchema(BaseModel):
    name: Optional[str] = None
    university: Optional[str] = None
    grade: Optional[float] = None
    bio: Optional[str] = None
    resume_url: Optional[str] = None

class RecruiterUpdateSchema(BaseModel):
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_details: Optional[str] = None
    bio: Optional[str] = None

# what you return when someone views a profile
class StudentProfileSchema(BaseModel):
    id: uuid.UUID
    name: str
    university: str
    grade: float
    bio: str
    resume_url: str
    profile_picture_url: Optional[str] = None

    


class RecruiterProfileSchema(BaseModel):
    id: uuid.UUID
    company_name: str
    company_website: Optional[str] = None
    company_details: Optional[str] = None
    profile_picture_url: Optional[str] = None
    company_logo_url: Optional[str] = None
    total_hired: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)