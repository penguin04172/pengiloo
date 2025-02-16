from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

import game
from web.arena import get_arena
from web.template_config import templates

router = APIRouter(prefix='/displays', tags=['displays'])


@router.get('/alliance_station')
async def alliance_station_display(request: Request, display_id: str = '', nickname: str = ''):
    path = await enforce_display_configuration(request, display_id, nickname, {'station': 'R1'})

    if path is not None:
        return RedirectResponse(path)

    return templates.TemplateResponse(
        request, 'display_alliance_station.html.jinja', {'settings': get_arena().event}
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

    return templates.TemplateResponse(
        request,
        'display_audience.html.jinja',
        {
            'settings': get_arena().event,
            'match_sounds': game.get_sounds(),
        },
    )


async def enforce_display_configuration(
    request: Request, display_id: str = '', nickname='', defaults: dict[str, str] = None
) -> str | None:
    all_present = True
    configuration = dict[str, str]()

    if display_id == '':
        display_id = get_arena().next_display_id()
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
