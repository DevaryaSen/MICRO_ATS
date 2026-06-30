Readme · MD
# microATS
 
A production-grade Applicant Tracking System REST API built with FastAPI and async Python. Students apply to jobs, recruiters manage hiring pipelines — all through a clean, role-based API.
 
---
 
## What it does
 
**Students** can browse jobs filtered by CGPA cutoff and university, apply to up to 6 jobs, and track their application stage in real time.
 
**Recruiters** can post up to 12 jobs (unlocking 6 more per successful hire), view all applicants, inspect student profiles, and move candidates through a structured hiring pipeline.
 
---
 
## Stack
 
| Layer | Technology |
|---|---|
| Framework | FastAPI (async) |
| Database | PostgreSQL on Neon |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Auth | JWT via python-jose, pwdlib for hashing |
| Email | aiosmtplib + Brevo SMTP |
| File Storage | ImageKit CDN |
| Validation | Pydantic v2 |
| Runtime | Python 3.12+ |
 
---
 
## Features
 
**Auth**
- Student and recruiter registration with role separation
- JWT access + refresh token pair on login
- Password reset via email OTP (background task, non-blocking)
- Change password with current password verification
- RBAC via FastAPI `Depends` — routes enforce roles at the dependency level
**Jobs**
- Recruiters create, update, close, and delete jobs
- Per-recruiter job slot system: 12 base slots, +6 per confirmed hire (`total_hired`)
- Students browse all open jobs or filter to only eligible ones (CGPA + university cutoff)
- Jobs carry salary range, role type, deadline, and document attachment URL
**Applications**
- Students apply to jobs — server validates eligibility before inserting
- Hard limit of 6 applications per student, enforced at service layer
- Full pipeline: `APPLIED → SEEN → INTERVIEW → APPROVED → SELECTED / REJECTED`
- Recruiters move applicants through stages; students receive email on stage change
- Applicant count visible without exposing other applicants' identities
**Profiles**
- Students: name, university, CGPA, bio, resume URL, profile picture
- Recruiters: company name, website, details, workforce size, logo
- Partial updates via `PATCH` using `exclude_unset=True`
**File Uploads**
- Profile pictures (student + recruiter): JPEG/PNG/WEBP, max 2 MB
- Resumes (student): PDF only, max 5 MB
- Company logos (recruiter): JPEG/PNG/WEBP, max 2 MB
- All files uploaded to ImageKit CDN; only the URL is stored in the DB
---
 
## API Overview
 
```
Auth
  POST  /auth/register/student
  POST  /auth/register/recruiter
  POST  /auth/login
  POST  /auth/forgot-password
  POST  /auth/reset-password
  POST  /auth/change-password
 
Jobs
  GET   /jobs/                      anyone logged in
  GET   /jobs/{job_id}
  GET   /jobs/eligible/me           student only — filtered by CGPA + university
  POST  /jobs/                      recruiter only
  PATCH /jobs/{job_id}
  PATCH /jobs/{job_id}/close
  DELETE /jobs/{job_id}
 
Applications
  POST  /applications/apply/{job_id}         student
  GET   /applications/me                     student — own applications + stages
  GET   /applications/job/{job_id}           recruiter — all applicants for a job
  PATCH /applications/{application_id}/stage recruiter — move pipeline stage
 
Profiles
  GET   /profiles/student/me
  PATCH /profiles/student/me
  GET   /profiles/student/{student_id}
  GET   /profiles/recruiter/me
  PATCH /profiles/recruiter/me
  GET   /profiles/recruiter/{recruiter_id}
 
Uploads
  POST  /profiles/student/me/resume
  POST  /profiles/student/me/profile-picture
  POST  /profiles/recruiter/me/company-logo
```
 
---
 
## Project Structure
 
```
app/
├── Auth/
│   ├── auth_router.py
│   ├── AuthService.py
│   ├── Auth_Schema.py
│   └── utils.py              # JWT, password hashing, RBAC dependencies
├── Jobs/
│   ├── jobs_routers.py
│   ├── service.py
│   └── Jobs_schema.py
├── Application/
│   ├── application_router.py
│   ├── service.py
│   └── application_schemas.py
├── profile/
│   ├── profile_routers.py
│   ├── service.py
│   └── schemas.py
├── Upload/
│   ├── upload_service.py
│   └── upload_schemas.py
├── Utils/
│   └── email_utils.py        # aiosmtplib email sending + token generation
├── Database/
│   ├── Models.py             # SQLAlchemy models
│   └── database.py           # async engine + session factory
├── config.py                 # Pydantic settings
└── main.py
alembic/
├── env.py
└── versions/
```
 
---
 
## Local Setup
 
```bash
# clone
git clone https://github.com/your-username/microats.git
cd microats
 
# create venv and install
python -m venv .venv
source .venv/bin/activate
pip install uv
uv sync
 
# configure env
cp .env.example .env
# fill in your values (see Configuration below)
 
# run migrations
alembic upgrade head
 
# start server
uvicorn app.main:app --reload
```
 
Open `http://localhost:8000/docs` for the interactive API explorer.
 
---
 
## Configuration
 
Copy `.env.example` to `.env` and fill in:
 
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?ssl=require
 
# Auth
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RESET_TOKEN_EXPIRE_MINUTES=60
 
# Email (Brevo SMTP)
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your-brevo-smtp-key
MAIL_FROM=noreply@yourdomain.com
MAIL_USE_TLS=true
 
# ImageKit
IMAGEKIT_PRIVATE_KEY=your-private-key
IMAGEKIT_PUBLIC_KEY=your-public-key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your-id
 
# Frontend (for reset password links)
FRONTEND_URL=http://localhost:3000
```
 
---
 
## Data Model
 
```
User ──┬── Student ──── Application ──── Job ──── Recruiter
       │                    │
       └── Recruiter        └── ApplicationStage enum
                                (APPLIED → SEEN → INTERVIEW
                                 → APPROVED → SELECTED / REJECTED)
 
PasswordResetToken ──── User
```
 
---
 
## Business Rules
 
| Rule | Detail |
|---|---|
| Student application limit | Max 6 total applications |
| Recruiter job slot base | 12 active jobs |
| Job slot unlock | +6 per `SELECTED` applicant (`total_hired` column) |
| Eligibility check | CGPA ≥ `cutoff_cgpa` AND university matches `cutoff_school` |
| Duplicate application | Blocked at service layer (409 Conflict) |
| Closed job | Applications blocked (400 Bad Request) |
| Resume type | PDF only, max 5 MB |
| Image type | JPEG / PNG / WEBP, max 2 MB |
 
---
