from fastapi import APIRouter
from .endpoints import admin_mysteries, mysteries, gameplay

api_router = APIRouter()
api_router.include_router(admin_mysteries.router, tags=["Admin - Mysteries"])
api_router.include_router(mysteries.router, tags=["Public - Mysteries"])
api_router.include_router(gameplay.router, tags=["Public - Gameplay"])
