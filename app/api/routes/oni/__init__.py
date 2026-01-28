"""
ONI Routes Package v7.0
Modular API routes for ONI Enhanced Cognitive Edition.
"""

from fastapi import APIRouter

# Create main router
router = APIRouter(prefix="", tags=["oni"])

# Import and include modular sub-routers
from app.api.routes.oni.vision import router as vision_router
from app.api.routes.oni.window import router as window_router
from app.api.routes.oni.actions import router as actions_router
# from app.api.routes.oni.smart import router as smart_router
from app.api.routes.oni.memory import router as memory_router
from app.api.routes.oni.canvas import router as canvas_router
from app.api.routes.oni.errors import router as errors_router
from app.api.routes.oni.recovery import router as recovery_router
from app.api.routes.oni.adapter import router as adapter_router
from app.api.routes.oni.task import router as task_router

# v7.0 Enhanced Cognitive Routes
# from app.api.routes.oni.v7 import router as v7_router

# v17.0 ArtMaster - Pure GUI Automation
from app.api.routes.oni.artmaster import router as artmaster_router

router.include_router(vision_router)
router.include_router(window_router)
router.include_router(actions_router)
# router.include_router(smart_router)
router.include_router(memory_router)
router.include_router(canvas_router)
router.include_router(errors_router)
router.include_router(recovery_router)
router.include_router(adapter_router)
router.include_router(task_router)

# v7.0 Endpoints
# router.include_router(v7_router)

# v17.0 ArtMaster Endpoints
router.include_router(artmaster_router)

# v23.0 Autonomous Executor - Elimina Memória Episódica
from app.api.routes.oni.autonomous import router as autonomous_router
router.include_router(autonomous_router)

# v23.1 Adaptive Sovereign - UBIE + ONI + ANT Fusion
from app.api.routes.oni.sovereign import router as sovereign_router
router.include_router(sovereign_router)

# v24.0 Universal Self-Healing Engine
from app.api.routes.oni.healing import router as healing_router
router.include_router(healing_router)

__all__ = ["router"]

