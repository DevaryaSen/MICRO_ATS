Viewed upload_service.py:42-65

# MicroATS – AI‑Powered Academic Talent System  

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)  
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)  
[![ImageKit SDK 5.x](https://img.shields.io/badge/ImageKit‑SDK%205.x‑orange.svg)](https://github.com/imagekit-developer/imagekit-python)  

## Table of Contents
- [Overview](#overview)  
- [Key Features](#key-features)  
- [Architecture Highlights](#architecture-highlights)  
- [Quick Start (Local Development)](#quick-start-local-development)  
- [Configuration](#configuration)  
- [API Endpoints](#api-endpoints)  
- [File‑Upload Validation Rules](#file‑upload-validation-rules)  
- [Running the Automated Test Suite](#running-the-automated-test-suite)  
- [Project Structure](#project-structure)  
- [Future Enhancements](#future-enhancements)  
- [Contributing](#contributing)  

---

## Overview
MicroATS is a **FastAPI‑based backend** that powers an academic‑talent marketplace. It provides secure authentication, role‑based profile management, and **robust file‑upload services** (resumes, profile pictures, company logos) backed by **ImageKit** for fast CDN delivery.

The codebase follows a **modular Service/Router/Schema** pattern, making each concern isolated, testable, and easy to extend.

---

## Key Features
| Feature | Description |
|---------|-------------|
| **JWT‑based auth** – login / registration for students & recruiters. |
| **Typed Pydantic schemas** for request/response validation. |
| **ImageKit integration** – server‑side uploads using the official Python SDK (v5). |
| **Strict file validation** – MIME type & size limits (PDF ≤ 5 MB, images ≤ 2 MB). |
| **Comprehensive test suite** – end‑to‑end upload tests covering auth, validation, and success paths. |
| **Extensible service layer** – each router delegates to a dedicated service class. |
| **Environment‑driven config** – `.env` holds secrets (`IMAGEKIT_PRIVATE_KEY`, `IMAGEKIT_URL_ENDPOINT`, etc.). |

---

## Architecture Highlights
- **`app/Upload/`** – core upload logic.  
  - `upload_service.py` — validates files, streams raw bytes to ImageKit (uses `io.BytesIO`).  
  - `upload_schemas.py` — enumerations of allowed MIME types, size constants, and response model.  
- **`app/profile/`** – profile CRUD & URL‑update helpers.  
- **`app/Auth/`** – JWT generation, password hashing, user‑registration schemas.  
- **`app/Database/`** – async SQLAlchemy models (PostgreSQL via `DATABASE_URL`).  

All services are **stateless** and can be plugged into any FastAPI router.

---

## Quick Start (Local Development)

```bash
# 1️⃣ Clone the repo
git clone https://github.com/your‑username/microats.git
cd microats

# 2️⃣ Create a virtual env (python 3.12+)
python -m venv .venv
source .venv/bin/activate

# 3️⃣ Install dependencies (includes imagekitio)
uv pip install -r requirements.txt

# 4️⃣ Set up environment variables
cp .env.example .env
# Edit .env → add your ImageKit private key and URL endpoint, plus DB URL, JWT secret, etc.

# 5️⃣ Run migrations (if using Alembic) – optional for a fresh SQLite demo
uv run alembic upgrade head

# 6️⃣ Launch the API
uv run uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> for the interactive OpenAPI UI.

---

## Configuration

| Variable | Purpose | Example |
|----------|---------|---------|
| `IMAGEKIT_PRIVATE_KEY` | ImageKit **server‑side** secret (required). | `private_OUJSA2AbIRETgwnLdewMmyhZ8H8=` |
| `IMAGEKIT_URL_ENDPOINT` | Base URL for generated assets. | `https://ik.imagekit.io/5hpsqmj5w` |
| `DATABASE_URL` | Async PostgreSQL connection string. | `postgresql+asyncpg://user:pass@host/db` |
| `SECRET_KEY` | JWT signing secret. | `supersecretkey123` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` / `REFRESH_TOKEN_EXPIRE_DAYS` | Token lifetimes. | `30` / `7` |

All variables are loaded via **Pydantic `BaseSettings`** in `app/config.py`.

---

## API Endpoints (excerpt)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/register/student` | ✖️ | Register a student (resume upload optional). |
| `POST` | `/auth/login` | ✖️ | Obtain JWT access/refresh tokens. |
| `POST` | `/profiles/student/me/resume` | ✅ | Upload a PDF resume (≤ 5 MB). |
| `POST` | `/profiles/student/me/profile-picture` | ✅ | Upload a profile picture (PNG/JPG/WEBP ≤ 2 MB). |
| `POST` | `/profiles/recruiter/me/company-logo` | ✅ | Upload a company logo (same constraints as picture). |

All upload routes return the **`UploadResponse`** model defined in  
`[upload_schemas.py](file:///Users/devaryasen/Desktop/PYTHON_PROJECTS/MICROATS/app/Upload/upload_schemas.py)`.

---

## File‑Upload Validation Rules  

Implemented in `UploadService._validate_file` (lines 42‑65 of `upload_service.py`):

| Parameter | Allowed MIME types | Max size |
|-----------|-------------------|----------|
| **Resume** | `application/pdf` | **5 MB** |
| **Image** (profile picture & logo) | `image/jpeg`, `image/jpg`, `image/png`, `image/webp` | **2 MB** |

If a file fails validation, the API returns **HTTP 422 (Unprocessable Content)** with a clear error message (e.g., `"Invalid resume type: 'text/plain'. Allowed: application/pdf"`).

---

## Running the Automated Test Suite  

The repository ships with a **full upload test suite** (`run_all_upload_tests.sh`) that:

1. Registers a test student and obtains a JWT.  
2. Executes seven scenarios (auth missing, wrong MIME type, oversized file, successful uploads, etc.).  
3. Asserts proper HTTP status codes and inspects ImageKit response URLs.

```bash
chmod +x scripts/run_all_upload_tests.sh
./scripts/run_all_upload_tests.sh
```

All tests currently pass:

```
✅ PASS [Valid PDF resume upload] → HTTP 200
✅ PASS [Valid PNG profile picture upload] → HTTP 200
...
```

The suite also confirms that **ImageKit receives raw byte streams**, not base64 strings, after the recent SDK‑v5 fix.

---

## Project Structure (high‑level)

```
micr​oats/
├─ app/
│  ├─ Auth/                # JWT, password utils, registration schemas
│  ├─ Database/            # async SQLAlchemy models & DB utils
│  ├─ Upload/               # <--- Core upload logic
│  │   ├─ upload_service.py   (service layer – validation + ImageKit upload)
│  │   └─ upload_schemas.py   (enums, size limits, response model)
│  ├─ profile/             # profile CRUD, URL update helpers
│  └─ config.py            # Pydantic settings loader
├─ tests/                  # pytest suite (unit + integration)
├─ scripts/                # helper scripts (e.g., run_all_upload_tests.sh)
├─ .env.example            # template for required env vars
└─ pyproject.toml          # poetry/uv project metadata
```

Key files you may want to read:

- **Upload service** – `[upload_service.py](file:///Users/devaryasen/Desktop/PYTHON_PROJECTS/MICROATS/app/Upload/upload_service.py)`  
- **Upload schemas** – `[upload_schemas.py](file:///Users/devaryasen/Desktop/PYTHON_PROJECTS/MICROATS/app/Upload/upload_schemas.py)`  
- **Profile router** – `[profile_routers.py](file:///Users/devaryasen/Desktop/PYTHON_PROJECTS/MICROATS/app/profile/profile_routers.py)`  

---

## Future Enhancements
- **Batch upload endpoints** for bulk resume imports.  
- **Presigned URLs** for client‑side direct uploads (reduces server load).  
- **Webhooks** to react to ImageKit events (e.g., versioning, automatic image optimization).  
- **Docker/Kubernetes** deployment manifests for production scaling.  

---

## Contributing
1. Fork the repo and create a feature branch.  
2. Install the dev dependencies (`uv pip install -r requirements-dev.txt`).  
3. Run tests (`uv run pytest`).  
4. Ensure new code follows the existing **service‑router‑schema** pattern and updates `UploadService._validate_file` if you introduce new file types.  

Open a PR with a clear description of the change and any required migration steps.

---

Enjoy building with MicroATS! If you run into any issues or have ideas for improvements, feel free to open an issue or submit a pull request.
