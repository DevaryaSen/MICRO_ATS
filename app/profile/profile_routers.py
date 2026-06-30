import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.Database.database import get_db
from app.Database.Models import User
from app.Auth.utils import get_current_user, require_student, require_recruiter
from app.profile.profile_service import ProfileService
from app.profile.profile_schema import StudentProfileSchema, StudentUpdateSchema, RecruiterProfileSchema, RecruiterUpdateSchema
from app.Upload.upload_service import UploadService
from app.Upload.upload_schemas import UploadResponse

router = APIRouter(prefix="/profiles", tags=["profiles"])


def get_profile_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


# ── Student ──────────────────────────────────────────────

@router.get("/student/me", response_model=StudentProfileSchema)
async def get_my_student_profile(
    current_user: User = Depends(require_student),
    service: ProfileService = Depends(get_profile_service)
):
    return await service.get_student_profile(current_user.id)


@router.patch("/student/me", response_model=StudentProfileSchema)
async def update_my_student_profile(
    data: StudentUpdateSchema,
    current_user: User = Depends(require_student),
    service: ProfileService = Depends(get_profile_service)
):
    return await service.update_student_profile(current_user.id, data.model_dump(exclude_unset=True))


@router.get("/student/{student_id}", response_model=StudentProfileSchema)
async def get_student_profile(
    student_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # any logged in user can view
    service: ProfileService = Depends(get_profile_service)
):
    return await service.get_student_profile(student_id)


# ── Recruiter ─────────────────────────────────────────────

@router.get("/recruiter/me", response_model=RecruiterProfileSchema)
async def get_my_recruiter_profile(
    current_user: User = Depends(require_recruiter),
    service: ProfileService = Depends(get_profile_service)
):
    return await service.get_recruiter_profile(current_user.id)


@router.patch("/recruiter/me", response_model=RecruiterProfileSchema)
async def update_my_recruiter_profile(
    data: RecruiterUpdateSchema,
    current_user: User = Depends(require_recruiter),
    service: ProfileService = Depends(get_profile_service)
):
    return await service.update_recruiter_profile(current_user.id, data.model_dump(exclude_unset=True))


@router.get("/recruiter/{recruiter_id}", response_model=RecruiterProfileSchema)
async def get_recruiter_profile(
    recruiter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service)
):
    return await service.get_recruiter_profile(recruiter_id)


# ── File Upload Endpoints ─────────────────────────────────

@router.post("/student/me/resume", response_model=UploadResponse)
async def upload_student_resume(
    file: UploadFile = File(..., description="PDF file, max 5 MB"),
    current_user: User = Depends(require_student),
    service: ProfileService = Depends(get_profile_service),
):
    """Upload or replace the current student's resume (PDF only, ≤ 5 MB)."""
    upload_svc = UploadService()
    result = await upload_svc.upload_resume(file, current_user.id)
    await service.update_student_resume_url(current_user.id, result.url)
    return result


@router.post("/student/me/profile-picture", response_model=UploadResponse)
async def upload_student_profile_picture(
    file: UploadFile = File(..., description="PNG/JPG/WEBP image, max 2 MB"),
    current_user: User = Depends(require_student),
    service: ProfileService = Depends(get_profile_service),
):
    """Upload or replace the current student's profile picture (PNG/JPG/WEBP, ≤ 2 MB)."""
    upload_svc = UploadService()
    result = await upload_svc.upload_profile_picture(file, current_user.id)
    await service.update_student_profile_picture(current_user.id, result.url)
    return result


@router.post("/recruiter/me/profile-picture", response_model=UploadResponse)
async def upload_recruiter_profile_picture(
    file: UploadFile = File(..., description="PNG/JPG/WEBP image, max 2 MB"),
    current_user: User = Depends(require_recruiter),
    service: ProfileService = Depends(get_profile_service),
):
    """Upload or replace the current recruiter's profile picture (PNG/JPG/WEBP, ≤ 2 MB)."""
    upload_svc = UploadService()
    result = await upload_svc.upload_profile_picture(file, current_user.id)
    await service.update_recruiter_profile_picture(current_user.id, result.url)
    return result


@router.post("/recruiter/me/company-logo", response_model=UploadResponse)
async def upload_recruiter_company_logo(
    file: UploadFile = File(..., description="PNG/JPG/WEBP image, max 2 MB"),
    current_user: User = Depends(require_recruiter),
    service: ProfileService = Depends(get_profile_service),
):
    """Upload or replace the current recruiter's company logo (PNG/JPG/WEBP, ≤ 2 MB)."""
    upload_svc = UploadService()
    result = await upload_svc.upload_company_logo(file, current_user.id)
    await service.update_recruiter_company_logo(current_user.id, result.url)
    return result

