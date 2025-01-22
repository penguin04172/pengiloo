import models

from .router import setup_router


@setup_router.get('/lower_thirds')
async def get_lower_thirds():
    lower_thirds = models.read_all_lower_thirds()
    return {'event_settings': models.read_event_settings(), 'lower_thirds': lower_thirds}
