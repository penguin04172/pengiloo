from pony.orm import Json, Optional, PrimaryKey, db_session

from game.ranking import Ranking

from .base import db


class RankingDB(db.Entity):
    team_id = PrimaryKey(int, auto=False)
    rank = Optional(int)
    previous_rank = Optional(int)
    fields = Optional(Json)


@db_session
def create_ranking(ranking: Ranking):
    if RankingDB.get(team_id=ranking.team_id) is not None:
        return None
    new_ranking = RankingDB(**ranking.model_dump(exclude_none=True))
    return Ranking(**new_ranking.to_dict())


@db_session
def read_ranking_for_team(team_id: int):
    ranking = RankingDB.get(team_id=team_id)
    return None if ranking is None else Ranking(**ranking.to_dict())


@db_session
def update_ranking(ranking: Ranking):
    ranking_data = RankingDB.get(team_id=ranking.team_id)
    if ranking_data is None:
        return None

    ranking_data.set(**ranking.model_dump(exclude_none=True))
    return Ranking(**ranking_data.to_dict())


@db_session
def delete_ranking(team_id: int):
    RankingDB[team_id].delete()


def truncate_ranking():
    db.drop_table(RankingDB._table_, with_all_data=True)
    db.create_tables(True)


@db_session
def read_all_rankings():
    rankings = RankingDB.select().order_by(RankingDB.rank)

    return [Ranking(**rank.to_dict()) for rank in rankings]


def replace_all_rankings(rankings: list[Ranking]):
    truncate_ranking()

    for rank in rankings:
        create_ranking(rank)
