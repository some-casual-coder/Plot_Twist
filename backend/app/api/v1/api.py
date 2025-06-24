from fastapi import APIRouter
from .endpoints import admin_mysteries

api_router = APIRouter()
api_router.include_router(admin_mysteries.router,
                          prefix="/admin", tags=["Admin - Mysteries"])
