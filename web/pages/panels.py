from fastapi import APIRouter, Request

from web.template_config import templates

router = APIRouter(prefix='/panels', tags=['panelsPage'])


@router.get('')
async def get_panels(request: Request):
    return templates.TemplateResponse(request, 'panels.html.jinja')
