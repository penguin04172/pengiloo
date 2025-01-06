from pony.orm import IntArray, Optional, PrimaryKey, db_session
from pydantic import BaseModel

from .base import db
from .match import Match


class AllianceSelectionRankedTeam(BaseModel):
    rank: int
    team_id: int
    picked: bool


class Alliance(BaseModel):
    id: int
    team_ids: list[int]
    line_up: list[int] = [0] * 3


class AllianceDB(db.Entity):
    id = PrimaryKey(int, auto=False)
    team_ids = Optional(IntArray)
    line_up = Optional(IntArray)


@db_session
def create_alliance(alliance: Alliance):
    if AllianceDB.get(id=alliance.id) is not None:
        return None
    new_alliance = AllianceDB(**alliance.model_dump(exclude_none=True))
    return Alliance(**new_alliance.to_dict())


@db_session
def read_alliance_by_id(id: int):
    alliance = AllianceDB.get(id=id)
    return Alliance(**alliance.to_dict()) if alliance is not None else None


@db_session
def update_alliance(alliance: Alliance):
    data = AllianceDB.get(id=alliance.id)
    if data is None:
        return None
    data.set(**alliance.model_dump(exclude_none=True))
    return Alliance(**data.to_dict())


@db_session
def delete_alliance(id: int):
    data = AllianceDB.get(id=id)
    if data is not None:
        data.delete()


def truncate_alliance():
    db.drop_table(table_name=AllianceDB._table_, with_all_data=True)
    db.create_tables()


@db_session
def read_all_alliances():
    alliances = AllianceDB.select()
    return [Alliance(**a.to_dict()) for a in alliances.order_by(AllianceDB.id)]


@db_session
def update_alliance_from_match(alliance_id: int, match_team_ids: list[int]):
    alliance = read_alliance_by_id(alliance_id)
    if alliance is None:
        return None

    changed = False
    if match_team_ids != alliance.line_up:
        alliance.line_up = match_team_ids
        changed = True

    for team_id in match_team_ids:
        if team_id not in alliance.team_ids:
            alliance.team_ids.append(team_id)
            changed = True

    if changed:
        alliance = update_alliance(alliance)

    return alliance


# Returns two arrays containing the IDs of any teams for the red and blue alliances, respectively, who are part of the
# playoff alliance but are not playing in the given match.
# If the given match isn't a playoff match, empty arrays are returned.
def read_off_field_team_ids(match: Match):
    red_off_field_teams = read_off_field_team_ids_for_alliance(
        match.playoff_red_alliance, match.red1, match.red2, match.red3
    )
    blue_off_field_teams = read_off_field_team_ids_for_alliance(
        match.playoff_blue_alliance, match.blue1, match.blue2, match.blue3
    )

    return red_off_field_teams, blue_off_field_teams


def read_off_field_team_ids_for_alliance(
    alliance_id: int, team_id_1: int, team_id_2: int, team_id_3: int
):
    if alliance_id == 0:
        return []

    alliance = read_alliance_by_id(alliance_id)
    if alliance is None:
        return None

    off_field_team_ids = []
    for alliance_team_id in alliance.team_ids:
        if alliance_team_id not in [team_id_1, team_id_2, team_id_3]:
            off_field_team_ids.append(alliance_team_id)

    return off_field_team_ids
