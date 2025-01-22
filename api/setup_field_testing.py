import game
import models

from .router import setup_router


@setup_router.get('/field_testing')
async def get_field_testing():
    return {
        'event_settings': models.read_event_settings(),
        'match_sounds': game.sounds,
    }
