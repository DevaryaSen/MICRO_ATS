from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.Auth.auth_router import router as auth_router
from app.profile.profile_routers import router as users_router
from app.Application.application_router import router as application_router
from app.Jobs.jobs_routers import router as Jobs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="MicroATS",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(application_router)
app.include_router(Jobs_router)


@app.get("/")
async def root():
    return {"message": "MicroATS API Running"}