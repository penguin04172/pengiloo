from fastapi import APIRouter

from field.display import DisplayType, display_type_names

router = APIRouter(prefix='/setup/displays', tags=['displays'])


@router.get('/')
async def get_display_type() -> dict[DisplayType, str]:
    return display_type_names
