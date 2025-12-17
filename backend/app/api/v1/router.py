from fastapi import APIRouter
from app.api.v1 import auth

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, tags=["Authentication"])

from app.api.v1 import users
api_router.include_router(users.router, tags=["Users"])

from app.api.v1 import admin
api_router.include_router(admin.router, tags=["Admin"])


