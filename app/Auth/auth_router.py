from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.Database.database import get_db
from app.Auth.Auth_Schema import StudentRegisterSchema, RecruiterRegisterSchema, LoginSchema, TokenResponse,ForgotPassword,ResetPasswordRequest,changePassword
from app.Auth.AuthService import AuthService
from app.Utils.email_utils import send_password_reset_email
from fastapi import BackgroundTasks
from app.Database.Models import User
from app.Auth.utils import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer,OAuth2PasswordRequestForm



def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/token")
async def login_for_docs(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    print("REACHED TOKEN ENDPOINT")
    print(form_data.username)

    return await service.login_user(
        form_data.username,
        form_data.password
    )
@router.post("/register/student", status_code=201)
async def register_student(
    data: StudentRegisterSchema,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register_student(data)


@router.post("/register/recruiter", status_code=201)
async def register_recruiter(
    data: RecruiterRegisterSchema,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register_recruiter(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginSchema,
    service: AuthService = Depends(get_auth_service)
):
    return await service.login_user(data.email, data.password)
@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPassword,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service)
):
    return await service.ForgotPassword(data, background_tasks)


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service)
):
    return await service.reset_password(data)


@router.post("/change-password")
async def change_password(
    data: changePassword,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    return await service.changePassword(data, current_user)