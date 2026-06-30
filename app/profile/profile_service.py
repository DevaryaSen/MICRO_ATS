from app.Database.Models import User,Student,Recruiter,RoleEnum
from app.Database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from sqlalchemy import select   

class ProfileService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_student_profile(self, student_id: int):
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    async def update_student_profile(self, student_id: int, update_data: dict):
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        for key, value in update_data.items():
            setattr(student, key, value)

        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def get_recruiter_profile(self, recruiter_id: int):
        result = await self.db.execute(select(Recruiter).where(Recruiter.id == recruiter_id))
        recruiter = result.scalar_one_or_none()
        if not recruiter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter not found")
        return recruiter

    async def update_recruiter_profile(self, recruiter_id: int, update_data: dict):
        result = await self.db.execute(select(Recruiter).where(Recruiter.id == recruiter_id))
        recruiter = result.scalar_one_or_none()
        if not recruiter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter not found")

        for key, value in update_data.items():
            setattr(recruiter, key, value)

        self.db.add(recruiter)
        await self.db.commit()
        await self.db.refresh(recruiter)
        return recruiter

    # ── Upload URL updaters ───────────────────────────────

    async def update_student_resume_url(self, student_id, url: str):
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        student.resume_url = url
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def update_student_profile_picture(self, student_id, url: str):
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        student.profile_picture_url = url
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def update_recruiter_profile_picture(self, recruiter_id, url: str):
        result = await self.db.execute(select(Recruiter).where(Recruiter.id == recruiter_id))
        recruiter = result.scalar_one_or_none()
        if not recruiter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter not found")
        recruiter.profile_picture_url = url
        self.db.add(recruiter)
        await self.db.commit()
        await self.db.refresh(recruiter)
        return recruiter

    async def update_recruiter_company_logo(self, recruiter_id, url: str):
        result = await self.db.execute(select(Recruiter).where(Recruiter.id == recruiter_id))
        recruiter = result.scalar_one_or_none()
        if not recruiter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter not found")
        recruiter.company_logo_url = url
        self.db.add(recruiter)
        await self.db.commit()
        await self.db.refresh(recruiter)
        return recruiter