from app.Auth.Auth_Schema import StudentRegisterSchema, RecruiterRegisterSchema
from app.Database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.Database.Models import User, Student, Recruiter, RoleEnum,PasswordResetToken
from fastapi import Depends, HTTPException, status
from sqlalchemy import select,delete
from app.Auth.utils import hash_password, verify_password, create_access_token, create_refresh_token,get_current_user,hash_reset_token,generate_reset_token
from app.Auth.Auth_Schema import TokenData,ResetPasswordRequest,changePassword,ForgotPassword
from fastapi import BackgroundTasks
from datetime import datetime,timedelta,UTC
from app.Utils.email_utils import send_password_reset_email
from app.config import settings
class AuthService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def register_student(self, data: StudentRegisterSchema):
        new_user = User(
            username=data.username,
            email=data.email,
            password=hash_password(data.password),
            role=RoleEnum.STUDENT
        )
        self.db.add(new_user)
        await self.db.flush()  # gets the id without committing

        new_student = Student(
            id=new_user.id,
            name=data.name,
            university=data.university,
            grade=data.grade,
            bio=data.bio,
            resume_url=data.resume_url or ""
        )
        self.db.add(new_student)
        await self.db.commit()

    async def register_recruiter(self, data: RecruiterRegisterSchema):
        new_user = User(
            username=data.username,
            email=data.email,
            password=hash_password(data.password),
            role=RoleEnum.RECRUITER

        )
        self.db.add(new_user)
        await self.db.flush()

        new_recruiter = Recruiter(
        id=new_user.id,
        company_name=data.company_name,
        company_website=data.company_website,
        company_details=data.company_details,
    )
        self.db.add(new_recruiter)
        await self.db.commit()

    async def login_user(self, email: str, password: str):
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token, access_expiry = create_access_token(user.id, user.role.value)
        refresh_token, refresh_expiry = create_refresh_token(user.id, user.role.value)

        return {
            "access_token": access_token,
            "access_token_expires": access_expiry,
            "refresh_token": refresh_token,
            "refresh_token_expires": refresh_expiry,
            "token_type": "bearer",
            "user_id": str(user.id),
            "role": user.role.value
        }
    async def ForgotPassword(self,data:ForgotPassword,backgroundTasK: BackgroundTasks):
        query = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        user = query.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        else:
            await self.db.execute(
            delete(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id,
            ),
        )

            token = generate_reset_token()
            token_hash = hash_reset_token(token)
            expires_at = datetime.now(UTC) + timedelta(
                minutes=settings.reset_token_expire_minutes,
            )

            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token_hash,
                expires_at=expires_at,
            )
            self.db.add(reset_token)
            await self.db.commit()

            backgroundTasK.add_task(
                send_password_reset_email,
                to_email=user.email,
                username=user.username,
                token=token,
            )

        return {
            "message": "If an account exists with this email, you will receive password reset instructions.",
        }
    async def reset_password(self,
        request_data: ResetPasswordRequest,
    ):
        token_hash = hash_reset_token(request_data.token)

        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token == token_hash,
            ),
        )
        reset_token = result.scalars().first()

        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        if reset_token.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            await self.db.delete(reset_token)
            await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        result = await self.db.execute(
            select(User).where(User.id == reset_token.user_id),
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        user.password = hash_password(request_data.new_password)

        await self.db.execute(
            delete(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id,
            ),
        )

        await self.db.commit()
        return {
            "message": "Password reset successfully. You can now log in with your new password.",
        }    
    async def changePassword(self,data:changePassword,user:User):
        verify = verify_password(data.current_password, user.password)
        if not verify:
            raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED)
        user.password = hash_password(data.new_password)
    
        await self.db.execute(
            delete(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id,
            ),
        )

        await self.db.commit()
        return {"message": "Password changed successfully"}

        





                