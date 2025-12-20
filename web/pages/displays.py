from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

import models
from web.template_config import templates
from game.match_sounds import get_sounds_list

router = APIRouter(prefix='/displays', tags=['displays'])


@router.get('/alliance_station')
async def alliance_station_display(request: Request, display_id: str = '', nickname: str = ''):
    path = await enforce_display_configuration(request, display_id, nickname, {'station': 'R1'})

    if path is not None:
        return RedirectResponse(path)

    event = models.read_event_settings()
    return templates.TemplateResponse(
        request, 'display_alliance_station.html.jinja', {'settings': event}
    )


@router.get('/audience')
async def audience_display(request: Request, display_id: str = '', nickname: str = ''):
    path = await enforce_display_configuration(
        request,
        display_id,
        nickname,
        {
            'background': '#0f0',
            'reversed': 'false',
            'overlayLocation': 'bottom',
        },
    )

    if path is not None:
        return RedirectResponse(path)

    event = models.read_event_settings()
    
    return templates.TemplateResponse(
        request,
        'display_audience.html.jinja',
        {
            'settings': event,
            'match_sounds': get_sounds_list(),
        },
    )


@router.get('/announcer')
async def announcer_display(request: Request, display_id: str = '', nickname: str = ''):
    """Announcer display page - redirects to API for WebSocket-based display."""
    path = await enforce_display_configuration(request, display_id, nickname, None)
    if path is not None:
        return RedirectResponse(path)
    
    # For displays without templates, render a simple iframe to the API
    event = models.read_event_settings()
    return templates.TemplateResponse(
        request,
        'display_generic.html.jinja',
        {'settings': event, 'api_path': '/api/displays/announcer', 'display_type': 'Announcer'}
    )


@router.get('/rankings')
async def rankings_display(request: Request, display_id: str = '', nickname: str = ''):
    """Rankings display page."""
    path = await enforce_display_configuration(request, display_id, nickname, {'scroll_ms_per_row': '1000'})
    if path is not None:
        return RedirectResponse(path)
    
    event = models.read_event_settings()
    return templates.TemplateResponse(
        request,
        'display_generic.html.jinja',
        {'settings': event, 'api_path': '/api/displays/rankings', 'display_type': 'Rankings'}
    )


@router.get('/bracket')
async def bracket_display(request: Request, display_id: str = '', nickname: str = ''):
    """Bracket display page."""
    path = await enforce_display_configuration(request, display_id, nickname, None)
    if path is not None:
        return RedirectResponse(path)
    
    event = models.read_event_settings()
    return templates.TemplateResponse(
        request,
        'display_generic.html.jinja',
        {'settings': event, 'api_path': '/api/displays/bracket', 'display_type': 'Bracket'}
    )


@router.get('/queueing')
async def queueing_display(request: Request, display_id: str = '', nickname: str = ''):
    """Queueing display page."""
    path = await enforce_display_configuration(request, display_id, nickname, None)
    if path is not None:
        return RedirectResponse(path)
    
    event = models.read_event_settings()
    return templates.TemplateResponse(
        request,
        'display_generic.html.jinja',
        {'settings': event, 'api_path': '/api/displays/queueing', 'display_type': 'Queueing'}
    )


@router.get('/field_monitor')
async def field_monitor_display(request: Request, display_id: str = '', nickname: str = ''):
    """Field monitor display page."""
    path = await enforce_display_configuration(request, display_id, nickname, None)
    if path is not None:
        return RedirectResponse(path)
    
    event = models.read_event_settings()
    return templates.TemplateResponse(
        request,
        'display_generic.html.jinja',
        {'settings': event, 'api_path': '/api/displays/field_monitor', 'display_type': 'Field Monitor'}
    )


async def enforce_display_configuration(
    request: Request, display_id: str = '', nickname='', defaults: dict[str, str] = None
) -> str | None:
    all_present = True
    configuration = dict[str, str]()

    if display_id == '':
        # Generate a simple display ID based on timestamp
        import time
        display_id = str(int(time.time() * 1000))
        all_present = False

    if nickname != '':
        configuration['nickname'] = nickname

    body = request.query_params
    print(body)
    if defaults is not None:
        for key, value in defaults.items():
            if key in body:
                configuration[key] = body[key]
            else:
                configuration[key] = value
                all_present = False

    if not all_present:
        query = urlencode(configuration)

        path = f'{request.url.path}?display_id={display_id}&{query}'
        return path

    return None
