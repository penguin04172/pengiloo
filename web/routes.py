from fastapi import APIRouter

from . import api, pages, reports, websocket_routes

router = APIRouter(prefix='')

router.include_router(pages.router)
router.include_router(reports.router)
router.include_router(api.router)
router.include_router(websocket_routes.router)
