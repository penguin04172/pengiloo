from fastapi import APIRouter

from . import displays, index, match, setup

router = APIRouter(prefix='')

router.include_router(index.router)
router.include_router(setup.router)
router.include_router(match.router)
router.include_router(displays.router)
