from fastapi import APIRouter

import models
from field.display import display_type_names

router = APIRouter(prefix='/setup/displays', tags=['displays'])


@router.get('/')
async def get_displays():
    return {
        'event_settings': models.read_event_settings(),
        'displays_type_names': display_type_names,
    }
