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


@router.get('/awards')
async def get_awards(request: Request):
    return templates.TemplateResponse(request, 'setup_awards.html.jinja')


@router.get('/lower_thirds')
async def get_lower_thirds(request: Request):
    return templates.TemplateResponse(request, 'setup_lower_thirds.html.jinja')


@router.get('/sponsor_slides')
async def get_sponsor_slides(request: Request):
    return templates.TemplateResponse(request, 'setup_sponsor_slides.html.jinja')


@router.get('/breaks')
async def get_breaks(request: Request):
    return templates.TemplateResponse(request, 'setup_breaks.html.jinja')


@router.get('/display')
async def get_displays(request: Request):
    return templates.TemplateResponse(request, 'setup_displays.html.jinja')


@router.get('/field')
async def get_field_testing(request: Request):
    return templates.TemplateResponse(request, 'setup_field_testing.html.jinja')
