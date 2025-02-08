from fastapi import Request, WebSocket

import field
from web.arena import get_arena


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

    body = await request.json()
    if defaults is not None:
        for key, value in defaults.items():
            if key in body:
                configuration[key] = body[key]
            else:
                configuration[key] = value
                all_present = False

    if not all_present:
        query = ''
        for key, value in configuration.items():
            query += f'&{key}={value}'

        path = f'{request.url.path}?display_id={display_id}{query}'
        return path

    return None


async def register_display(websocket: WebSocket) -> field.Display:
    query = websocket.query_params
    display_configuration = field.display_from_url(websocket.url.path, query)

    ip_address = websocket.headers.get('X-Real-IP', '')
    if ip_address == '':
        ip_address = websocket.client.host

    return await get_arena().register_display(display_configuration, ip_address)
