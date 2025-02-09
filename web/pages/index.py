from fastapi import APIRouter, Request

from web.template_config import templates

router = APIRouter(prefix='')


@router.get('/')
async def get_index(request: Request):
    return templates.TemplateResponse(request, 'index.html.jinja')
