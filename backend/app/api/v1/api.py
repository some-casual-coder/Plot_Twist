from fastapi import APIRouter
from .endpoints import admin_mysteries, mysteries

api_router = APIRouter()
api_router.include_router(admin_mysteries.router, tags=["Admin - Mysteries"])
api_router.include_router(mysteries.router, tags=["Public - Mysteries"])
