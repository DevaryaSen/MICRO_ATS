import uuid
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.Database.database import get_db
from app.Database.Models import Application, ApplicationStage, Job, JobStatus


class ApplicationService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def apply_job(self, job_id: uuid.UUID, current_user):
        existing = await self.db.execute(
            select(Application).where(
                Application.student_id == current_user.id,
                Application.job_id == job_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Already applied to this job")

        count_result = await self.db.execute(
            select(func.count()).select_from(Application).where(Application.student_id == current_user.id)
        )
        if count_result.scalar() >= 6:
            raise HTTPException(status_code=403, detail="Application limit reached")

        job_result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != JobStatus.OPEN:
            raise HTTPException(status_code=400, detail="Job is closed")

        new_application = Application(
            student_id=current_user.id,
            job_id=job_id,
            stage=ApplicationStage.APPLIED,
        )
        self.db.add(new_application)
        await self.db.commit()
        await self.db.refresh(new_application)
        return new_application

    async def get_my_applications(self, current_user):
        result = await self.db.execute(
            select(Application).where(Application.student_id == current_user.id)
        )
        return result.scalars().all()

    async def get_job_applicants(self, job_id: uuid.UUID, current_user):
        job_result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not your job")

        result = await self.db.execute(
            select(Application).where(Application.job_id == job_id)
        )
        return result.scalars().all()

    async def update_stage(self, application_id: uuid.UUID, stage: ApplicationStage, current_user):
        result = await self.db.execute(select(Application).where(Application.id == application_id))
        application = result.scalar_one_or_none()
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        job_result = await self.db.execute(select(Job).where(Job.id == application.job_id))
        job = job_result.scalar_one_or_none()
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not your job")

        application.stage = stage
        await self.db.commit()
        await self.db.refresh(application)
        return application