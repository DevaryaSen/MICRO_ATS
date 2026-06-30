from __future__ import annotations
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Enum as SQLEnum, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Database.database import Base
from app.config import settings

class RoleEnum(str, Enum):
    STUDENT = "student"
    RECRUITER = "recruiter"
    ADMIN = "admin"
class JobRole(str, Enum):
    # Engineering & Tech (4)
    SOFTWARE_ENGINEER = "Software Engineer"
    FRONTEND_ENGINEER = "Frontend Engineer"
    BACKEND_ENGINEER = "Backend Engineer"
    DEVOPS_ENGINEER = "DevOps Engineer"

    # Data & AI (3)
    DATA_SCIENTIST = "Data Scientist"
    DATA_ANALYST = "Data Analyst"
    DATA_ENGINEER = "Data Engineer"

    # Product & Design (2)
    PRODUCT_MANAGER = "Product Manager"
    UI_UX_DESIGNER = "UI/UX Designer"

    # Marketing (3)
    MARKETING_MANAGER = "Marketing Manager"
    SEO_SPECIALIST = "SEO Specialist"
    SOCIAL_MEDIA_MANAGER = "Social Media Manager"

    # Sales (2)
    SALES_EXECUTIVE = "Sales Executive"
    BDM = "Business Development Manager"

    # HR & Recruiting (2)
    HR_MANAGER = "HR Manager"
    TECHNICAL_RECRUITER = "Technical Recruiter"

    # Finance (2)
    FINANCIAL_ANALYST = "Financial Analyst"
    ACCOUNTANT = "Accountant"

    # Operations (2)
    OPERATIONS_MANAGER = "Operations Manager"
    SUPPLY_CHAIN_MANAGER = "Supply Chain Manager"
class JobStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"

class ApplicationStage(str, Enum):
    APPLIED = "applied"
    SEEN = "seen"
    INTERVIEW = "interview"
    APPROVED = "approved"
    SELECTED = "selected"
    REJECTED = "rejected"
class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(SQLEnum(RoleEnum,create_type=False), nullable=False)
    
    student_profile: Mapped[Optional["Student"]] = relationship(back_populates="user", uselist=False)
    recruiter_profile: Mapped[Optional["Recruiter"]] = relationship(back_populates="user", uselist=False)
    reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
class Student(Base):
    __tablename__ = "students" 
    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    university: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[float] = mapped_column(Float, nullable=False)
    bio: Mapped[str] = mapped_column(String(2500), nullable=False)
    profile_picture_url: Mapped[Optional[str]] = mapped_column(String(500))
    resume_url: Mapped[str] = mapped_column(String(500), nullable=False)
    user: Mapped["User"] = relationship(back_populates="student_profile")
    applications: Mapped[list["Application"]] = relationship(back_populates="student", cascade="all, delete-orphan")

class Recruiter(Base):
    __tablename__ = "recruiters"
    
    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_website: Mapped[Optional[str]] = mapped_column(String(255))
    company_details: Mapped[Optional[str]] = mapped_column(String(1000)) 
    total_work_force: Mapped[Optional[int]] = mapped_column(default=0)
    total_hired: Mapped[Optional[int]] = mapped_column(default=0)
    
    
    profile_picture_url: Mapped[Optional[str]] = mapped_column(String(500))
    company_logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    user: Mapped["User"] = relationship(back_populates="recruiter_profile")
    posted_jobs: Mapped[list["Job"]] = relationship(back_populates="recruiter", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    recruiter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recruiters.id"))
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    
    cutoff_cgpa: Mapped[Optional[float]] = mapped_column(Float)        # float not str
    cutoff_school: Mapped[Optional[str]] = mapped_column(String(255))
    pay_min: Mapped[Optional[int]] = mapped_column(Integer)
    pay_max: Mapped[Optional[int]] = mapped_column(Integer)
    
    status: Mapped[JobStatus] = mapped_column(SQLEnum(JobStatus,create_type=False), default=JobStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    job_docs_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    recruiter: Mapped["Recruiter"] = relationship(back_populates="posted_jobs")
    applications: Mapped[list["Application"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"))
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"))
    
    stage: Mapped[ApplicationStage] = mapped_column(SQLEnum(ApplicationStage,create_type=False), default=ApplicationStage.APPLIED)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    student: Mapped["Student"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship(back_populates="applications")
    updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), 
    default=lambda: datetime.now(UTC),
    onupdate=lambda: datetime.now(UTC))

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="reset_tokens")