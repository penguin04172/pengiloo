from fastapi import APIRouter, HTTPException

from models.match import *

router = APIRouter(prefix='/api/match', tags=['match'])


@router.post('/')
async def post_new_match(match_data: Match):
	if match_data.scheduled_time is None:
		raise HTTPException(422)

	if match_data.long_name is None:
		match match_data.type:
			case MATCH_TYPE.pratice:
				match_data.long_name = f'Pratice {match_data.type_order}'
			case MATCH_TYPE.qualification:
				match_data.long_name = f'Qualification {match_data.type_order}'
	elif match_data.long_name.split(' ')[0] not in [
		'Test',
		'Pratice',
		'Qualification',
		'Match',
		'Eighthfinal',
		'Quarterfinal',
		'Semifinal',
		'Final',
	]:
		raise HTTPException(422)

	if match_data.short_name is None:
		match match_data.type:
			case MATCH_TYPE.pratice:
				match_data.short_name = f'P{match_data.type_order}'
			case MATCH_TYPE.qualification:
				match_data.short_name = f'Q{match_data.type_order}'
	elif match_data.short_name[0] not in ['T', 'P', 'Q', 'M', 'E', 'S', 'F']:
		raise HTTPException(422)

	return create_match(match_data).model_dump()


@router.get('/')
async def get_all_matches():
	return read_all_matches()


# @router.get("/{id}")
# async def get_match_by_id(id: int):
#     try:
#         return read_match_by_id(id).model_dump()
#     except ObjectNotFound:
#         raise HTTPException(404, "Match not found")


@router.get('/{type}')
async def get_matches_by_type(type: str, hidden: bool | None = None):
	match_type = MATCH_TYPE[type]
	return read_matches_by_type(match_type, hidden)


@router.get('/{type}/{order}')
async def get_match_by_type_order(type: str, order: int):
	match_type = MATCH_TYPE[type]

	try:
		return read_match_by_type_order(match_type, order).model_dump()
	except ObjectNotFound:
		raise HTTPException(404, 'Match not found')


@router.put('/')
async def put_update_match(match_data: Match):
	try:
		return update_match(match_data).model_dump()
	except ObjectNotFound:
		raise HTTPException(404, 'Match not found')


@router.delete('/{id}')
async def delete_match_data(id: int):
	try:
		delete_match(id)
	except ObjectNotFound:
		raise HTTPException(404, 'Match not found')
