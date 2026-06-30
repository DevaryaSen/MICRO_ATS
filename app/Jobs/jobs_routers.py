import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.Database.database import get_db
from app.Database.Models import User
from app.Auth.utils import require_recruiter, require_student, get_current_user
from app.Jobs.jobs_service import JobService
from app.Jobs.Jobs_schema import CreateJobSchema, UpdateJobSchema, JobResponseSchema

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_job_service(db: AsyncSession = Depends(get_db)) -> JobService:
    return JobService(db)


# anyone logged in can browse jobs
@router.get("/", response_model=list[JobResponseSchema])
async def get_all_jobs(
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    return await service.get_all_jobs()


# get single job
@router.get("/{job_id}", response_model=JobResponseSchema)
async def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    return await service.get_job(job_id)


# student sees only eligible jobs
@router.get("/eligible/me", response_model=list[JobResponseSchema])
async def get_eligible_jobs(
    current_user: User = Depends(require_student),
    service: JobService = Depends(get_job_service)
):
    return await service.get_eligible_jobs_for_student(current_user.id)


# recruiter creates job
@router.post("/", response_model=JobResponseSchema, status_code=201)
async def create_job(
    data: CreateJobSchema,
    current_user: User = Depends(require_recruiter),
    service: JobService = Depends(get_job_service)
):
    return await service.create_job(data, current_user)


# recruiter updates job
@router.patch("/{job_id}", response_model=JobResponseSchema)
async def update_job(
    job_id: uuid.UUID,
    data: UpdateJobSchema,
    current_user: User = Depends(require_recruiter),
    service: JobService = Depends(get_job_service)
):
    return await service.update_job(job_id, data, current_user)


# recruiter closes job
@router.patch("/{job_id}/close")
async def close_job(
    job_id: uuid.UUID,
    current_user: User = Depends(require_recruiter),
    service: JobService = Depends(get_job_service)
):
    return await service.close_job(job_id, current_user)


# recruiter deletes job
@router.delete("/{job_id}")
async def delete_job(
    job_id: uuid.UUID,
    current_user: User = Depends(require_recruiter),
    service: JobService = Depends(get_job_service)
):
    return await service.delete_job(job_id, current_user)