from pydantic import BaseModel, ConfigDict, EmailStr, Field 
import uuid
from app.Database.Models import JobRole,JobStatus
from datetime import datetime

class CreateJobSchema(BaseModel):
    title: str
    description: str
    cutoff_cgpa: float | None = None
    cutoff_school: str | None = None
    pay_min: int | None = None
    pay_max: int | None = None


class UpdateJobSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    cutoff_cgpa: float | None = None
    cutoff_school: str | None = None
    pay_min: int | None = None
    pay_max: int | None = None
class JobResponseSchema(BaseModel):
    id: uuid.UUID          # str → uuid.UUID
    title: str
    description: str
    cutoff_cgpa: float | None = None
    cutoff_school: str | None = None
    pay_min: int | None = None
    pay_max: int | None = None
    status: JobStatus
    created_at: datetime
    deadline: datetime | None = None
    recruiter_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
