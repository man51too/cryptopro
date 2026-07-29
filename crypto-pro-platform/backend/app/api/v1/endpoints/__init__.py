"""
API Endpoints Package
Exports all endpoint routers
"""

from .coins import router as coins_router
from .ai_predictions import router as ai_predictions_router
from .dashboard import router as dashboard_router

__all__ = [
    "coins_router",
    "ai_predictions_router",
    "dashboard_router",
]
