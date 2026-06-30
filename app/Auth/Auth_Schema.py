
import datetime
from typing import Annotated, Literal,Optional
from pydantic import BaseModel, Field,EmailStr
from datetime import datetime
class StudentRegisterSchema(BaseModel):
    username: str
    email: str
    password: str

    name: str
    university: str
    grade: float
    bio: str
    resume_url: Optional[str] = None
class RecruiterRegisterSchema(BaseModel):
    # User fields
    username: str
    email: str
    password: str
    
    # Recruiter profile fields — must match Recruiter model exactly
    company_name: str
    company_website: Optional[str] = None
    company_details: Optional[str] = None

class LoginSchema(BaseModel):
    email: str
    password: str

class TokenPayload(BaseModel):
    sub: str                          # user_id as string
    role: Literal["student", "recruiter", "admin"]
    token_type: Literal["access", "refresh"]
    exp: datetime
    iat: datetime
    jti: str | None = None            # optional: unique token ID for revocation

class TokenData(BaseModel):
    sub: str
    role: str
    token_type: str
    jti: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    role: str
    token_type: str
    user_id: str
    access_token_expires: datetime
    refresh_token_expires: datetime

class ForgotPassword(BaseModel):
    email: EmailStr
class changePassword(BaseModel):
    current_password: str
    new_password: str
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

