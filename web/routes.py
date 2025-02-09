from fastapi import APIRouter

from . import api, pages, reports

router = APIRouter(prefix='')

router.include_router(pages.router)
router.include_router(reports.router)
router.include_router(api.router)
