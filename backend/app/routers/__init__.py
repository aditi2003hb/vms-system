"""
API Routers Package
"""
from .admin import router as admin_router
from .users import router as users_router
from .clients import router as clients_router

__all__ = ['admin_router', 'users_router', 'clients_router']