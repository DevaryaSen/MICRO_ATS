import uuid
from app.Jobs.Jobs_schema import CreateJobSchema, UpdateJobSchema
from app.Database.Models import Job, Student, JobStatus
from app.Database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status


class JobService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def create_job(self, data: CreateJobSchema, current_user):
        new_job = Job(
            title=data.title,
            description=data.description,
            cutoff_cgpa=data.cutoff_cgpa,
            cutoff_school=data.cutoff_school,
            pay_min=data.pay_min,
            pay_max=data.pay_max,
            recruiter_id=current_user.id
        )
        self.db.add(new_job)
        await self.db.commit()
        await self.db.refresh(new_job)
        return new_job

    async def update_job(self, job_id: uuid.UUID, data: UpdateJobSchema, current_user):
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own jobs")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(job, key, value)

        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_job(self, job_id: uuid.UUID):
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return job

    async def get_all_jobs(self):
        result = await self.db.execute(select(Job))
        return result.scalars().all()

    async def delete_job(self, job_id: uuid.UUID, current_user):
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own jobs")

        await self.db.delete(job)
        await self.db.commit()
        return {"detail": "Job deleted successfully"}

    async def close_job(self, job_id: uuid.UUID, current_user):
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only close your own jobs")

        job.status = JobStatus.CLOSED
        await self.db.commit()
        return {"detail": "Job closed"}

    async def get_eligible_jobs_for_student(self, student_id: uuid.UUID):
        student_result = await self.db.execute(select(Student).where(Student.id == student_id))
        student = student_result.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        result = await self.db.execute(
            select(Job).where(
                (Job.cutoff_cgpa == None) | (Job.cutoff_cgpa <= student.grade),
                (Job.cutoff_school == None) | (Job.cutoff_school == student.university),
                Job.status == JobStatus.OPEN
            )
        )
        return result.scalars().all()