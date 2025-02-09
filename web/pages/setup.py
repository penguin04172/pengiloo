from fastapi import APIRouter, Request

from web.template_config import templates

router = APIRouter(prefix='/setup')


@router.get('/settings')
async def get_settings(request: Request):
    return templates.TemplateResponse(request, 'setup_settings.html.jinja')


@router.get('/teams')
async def get_teams(request: Request):
    return templates.TemplateResponse(request, 'setup_teams.html.jinja')


@router.get('/schedule')
async def get_schedule(request: Request):
    return templates.TemplateResponse(request, 'setup_schedule.html.jinja')
