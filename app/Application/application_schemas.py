import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.Database.Models import ApplicationStage


class ApplyJobSchema(BaseModel):
    job_id: uuid.UUID


class StageUpdateSchema(BaseModel):
    stage: ApplicationStage


class ApplicationResponseSchema(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    job_id: uuid.UUID
    stage: ApplicationStage
    applied_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)