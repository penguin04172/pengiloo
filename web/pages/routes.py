from fastapi import APIRouter

from . import index, setup

router = APIRouter(prefix='')

router.include_router(index.router)
router.include_router(setup.router)
