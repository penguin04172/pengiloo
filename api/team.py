from fastapi import APIRouter, HTTPException

from models.team import *

router = APIRouter(prefix='/api/team', tags=['teams'])


@router.get('/')
async def get_all():
	return read_all_teams()


@router.get('/{id}')
async def get_by_id(id: int):
	try:
		return read_team_by_id(id)
	except ObjectNotFound:
		raise HTTPException(404, 'Team not found')


@router.post('/')
async def post_new(team: Team):
	team_data = create_team(team)
	if team_data is None:
		raise HTTPException(400, 'Team exists')
	else:
		return team_data


@router.delete('/{id}')
async def delete_by_id(id: int):
	try:
		delete_team(id)
	except ObjectNotFound:
		raise HTTPException(404, 'Team not found')

	return {'message': 'success'}


@router.put('/')
async def put_update(team: Team):
	try:
		return update_team(team)
	except ObjectNotFound:
		raise HTTPException(404, 'Team not found')
