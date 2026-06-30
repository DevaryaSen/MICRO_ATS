import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.Database.database import get_db
from app.Database.Models import User, ApplicationStage
from app.Auth.utils import require_student, require_recruiter
from app.Application.application_service import ApplicationService
from app.Application.application_schemas import ApplicationResponseSchema, StageUpdateSchema

router = APIRouter(prefix="/applications", tags=["applications"])


def get_application_service(db: AsyncSession = Depends(get_db)) -> ApplicationService:
    return ApplicationService(db)


# student applies to a job
@router.post("/apply/{job_id}", response_model=ApplicationResponseSchema)
async def apply_job(
    job_id: uuid.UUID,
    current_user: User = Depends(require_student),
    service: ApplicationService = Depends(get_application_service)
):
    return await service.apply_job(job_id, current_user)


# student sees their own applications
@router.get("/me", response_model=list[ApplicationResponseSchema])
async def get_my_applications(
    current_user: User = Depends(require_student),
    service: ApplicationService = Depends(get_application_service)
):
    return await service.get_my_applications(current_user)


# recruiter sees all applicants for a job
@router.get("/job/{job_id}", response_model=list[ApplicationResponseSchema])
async def get_job_applicants(
    job_id: uuid.UUID,
    current_user: User = Depends(require_recruiter),
    service: ApplicationService = Depends(get_application_service)
):
    return await service.get_job_applicants(job_id, current_user)


# recruiter updates applicant stage
@router.patch("/{application_id}/stage", response_model=ApplicationResponseSchema)
async def update_stage(
    application_id: uuid.UUID,
    data: StageUpdateSchema,
    current_user: User = Depends(require_recruiter),
    service: ApplicationService = Depends(get_application_service)
):
    return await service.update_stage(application_id, data.stage, current_user)