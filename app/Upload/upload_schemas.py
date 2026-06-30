"""Pydantic schemas and constants for file upload validation."""

from enum import Enum
from pydantic import BaseModel


# ── Allowed MIME types ────────────────────────────────────

class AllowedImageType(str, Enum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    JPG = "image/jpg"
    WEBP = "image/webp"


class AllowedResumeType(str, Enum):
    PDF = "application/pdf"


# ── Size limits ───────────────────────────────────────────

MAX_RESUME_SIZE_MB: int = 5
MAX_IMAGE_SIZE_MB: int = 2

MAX_RESUME_SIZE_BYTES: int = MAX_RESUME_SIZE_MB * 1024 * 1024
MAX_IMAGE_SIZE_BYTES: int = MAX_IMAGE_SIZE_MB * 1024 * 1024


# ── Response schema ───────────────────────────────────────

class UploadResponse(BaseModel):
    """Returned to the client after a successful upload."""
    file_id: str
    url: str
    file_name: str
    file_type: str
    size: int
