from fastapi import APIRouter

router = APIRouter(prefix='')


@router.get('/')
async def get_index():
    return {'message': 'Hello World'}
