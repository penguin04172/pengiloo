from fastapi import APIRouter, Request

from web.template_config import templates

router = APIRouter(prefix='/match', tags=['matchPage'])


@router.get('/review')
async def get_review(request: Request):
    return templates.TemplateResponse(request, 'match_review.html.jinja', {})


@router.get('/logs')
async def get_result(request: Request):
    return templates.TemplateResponse(request, 'match_logs.html.jinja', {})
