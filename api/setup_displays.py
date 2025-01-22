import models
from field.display import display_type_names

from .router import setup_router


@setup_router.get('/displays')
async def get_displays():
    return {
        'event_settings': models.read_event_settings(),
        'displays_type_names': display_type_names,
    }
