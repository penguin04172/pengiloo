from fastapi import APIRouter, Request

from web.arena import get_arena
from web.template_config import templates

router = APIRouter(prefix='/match', tags=['matchPage'])


@router.get('/review')
async def get_review(request: Request):
    return templates.TemplateResponse(request, 'match_review.html.jinja', {})


@router.get('/logs')
async def get_result(request: Request):
    return templates.TemplateResponse(request, 'match_logs.html.jinja', {})


@router.get('/control')
async def get_control(request: Request):
    return templates.TemplateResponse(
        request,
        'match_control.html.jinja',
        {'settings': get_arena().event, 'plc_is_enabled': False, 'plc_armor_block_statuses': {}},
    )
