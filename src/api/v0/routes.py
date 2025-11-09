from fastapi import APIRouter

from .config_controller import router as config_router
from .hello import router as hello

from .message_controller import router as message_controller
from .action_controller import router as action_controller

router = APIRouter()
router.include_router(config_router)
router.include_router(hello)
router.include_router(message_controller)
router.include_router(action_controller)
