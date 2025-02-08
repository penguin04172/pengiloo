from fastapi import APIRouter

from . import api, index, reports

router = APIRouter(prefix='')

router.include_router(index.router)
router.include_router(reports.router)
router.include_router(api.router)
