"""Service layer for validating and uploading files to ImageKit."""

from __future__ import annotations

import io
import uuid
from enum import Enum

from fastapi import HTTPException, UploadFile, status
from imagekitio import ImageKit

from app.config import settings
from app.Upload.upload_schemas import (
    AllowedImageType,
    AllowedResumeType,
    MAX_IMAGE_SIZE_BYTES,
    MAX_RESUME_SIZE_BYTES,
    UploadResponse,
)


def _get_imagekit_client() -> ImageKit:
    """Lazily build an ImageKit client from app settings."""
    return ImageKit(
        private_key=settings.imagekit_private_key,
    )


class UploadService:
    """Validates files and uploads them to ImageKit."""

    def __init__(self) -> None:
        self.ik = _get_imagekit_client()

    # ── Internal helpers ──────────────────────────────────

    @staticmethod
    async def _validate_file(
        file: UploadFile,
        allowed_types: type[Enum],
        max_size_bytes: int,
        label: str = "file",
    ) -> bytes:
        """Read, validate content-type & size, and return raw bytes.

        Raises HTTPException 422 on validation failure.
        """
        # 1. Content-type check
        allowed_values = {t.value for t in allowed_types}
        if file.content_type not in allowed_values:
            nice = ", ".join(sorted(allowed_values))
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Invalid {label} type: '{file.content_type}'. Allowed: {nice}",
            )

        # 2. Read bytes
        contents = await file.read()

        # 3. Size check
        if len(contents) > max_size_bytes:
            max_mb = max_size_bytes / (1024 * 1024)
            actual_mb = round(len(contents) / (1024 * 1024), 2)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"{label.capitalize()} too large: {actual_mb} MB. "
                    f"Maximum allowed: {max_mb} MB."
                ),
            )

        return contents

    def _upload_to_imagekit(
        self,
        file_bytes: bytes,
        file_name: str,
        folder: str,
        content_type: str,
    ) -> UploadResponse:
        """Push bytes to ImageKit and return a typed response."""
        # SDK v5 expects raw bytes (as a file-like object) not base64
        result = self.ik.files.upload(
            file=(file_name, io.BytesIO(file_bytes), content_type),
            file_name=file_name,
            folder=folder,
            use_unique_file_name=True,
        )

        file_id = getattr(result, "file_id", None)
        url = getattr(result, "url", None)
        name = getattr(result, "name", None)
        size = getattr(result, "size", None)

        return UploadResponse(
            file_id=str(file_id),
            url=str(url),
            file_name=str(name),
            file_type=content_type,
            size=int(size),
        )

    # ── Public API ────────────────────────────────────────

    async def upload_resume(
        self,
        file: UploadFile,
        user_id: uuid.UUID,
    ) -> UploadResponse:
        """Validate (PDF, ≤5 MB) and upload a resume."""
        contents = await self._validate_file(
            file,
            allowed_types=AllowedResumeType,
            max_size_bytes=MAX_RESUME_SIZE_BYTES,
            label="resume",
        )
        return self._upload_to_imagekit(
            file_bytes=contents,
            file_name=file.filename or "resume.pdf",
            folder=f"/resumes/{user_id}",
            content_type=file.content_type or "application/pdf",
        )

    async def upload_profile_picture(
        self,
        file: UploadFile,
        user_id: uuid.UUID,
    ) -> UploadResponse:
        """Validate (PNG/JPG/WEBP, ≤2 MB) and upload a profile picture."""
        contents = await self._validate_file(
            file,
            allowed_types=AllowedImageType,
            max_size_bytes=MAX_IMAGE_SIZE_BYTES,
            label="profile picture",
        )
        return self._upload_to_imagekit(
            file_bytes=contents,
            file_name=file.filename or "profile.png",
            folder=f"/profile-pictures/{user_id}",
            content_type=file.content_type or "image/png",
        )

    async def upload_company_logo(
        self,
        file: UploadFile,
        user_id: uuid.UUID,
    ) -> UploadResponse:
        """Validate (PNG/JPG/WEBP, ≤2 MB) and upload a company logo."""
        contents = await self._validate_file(
            file,
            allowed_types=AllowedImageType,
            max_size_bytes=MAX_IMAGE_SIZE_BYTES,
            label="company logo",
        )
        return self._upload_to_imagekit(
            file_bytes=contents,
            file_name=file.filename or "logo.png",
            folder=f"/company-logos/{user_id}",
            content_type=file.content_type or "image/png",
        )
