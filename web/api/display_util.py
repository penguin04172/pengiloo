from fastapi import Request, WebSocket

import field
from web import arena_commands, arena_state


async def enforce_display_configuration(
    request: Request, display_id: str = '', nickname='', defaults: dict[str, str] = None
) -> str | None:
    all_present = True
    configuration = dict[str, str]()

    if display_id == '':
        # Get next display ID from state
        state = arena_state.get_full_state()
        next_id = state.get('next_display_id', 100)
        display_id = str(next_id)
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
    query = dict(websocket.query_params)

    display_configuration = field.display_from_url(websocket.url.path, query)

    ip_address = websocket.headers.get('X-Real-IP', '')
    if ip_address == '':
        ip_address = websocket.client.host

    # Send register command to Arena via IPC
    arena_commands.register_display(display_configuration.model_dump(), ip_address)
    
    # Return a basic Display object (actual registration happens in Arena)
    return field.Display(
        display_configuration=display_configuration,
        ip_address=ip_address
    )
