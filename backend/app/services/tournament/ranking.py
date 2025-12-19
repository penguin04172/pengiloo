from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete
from backend.app.models.match_result import MatchResult
from backend.app.models.match import Match, MatchType
from backend.app.models.ranking import Ranking


async def calculate_rankings(session: AsyncSession) -> List[Ranking]:
    # 1. Fetch all completed qualification matches
    result = await session.execute(select(MatchResult))
    match_results = result.scalars().all()

    match_result_map = await session.execute(select(Match))
    matches = {m.id: m for m in match_result_map.scalars().all()}

    team_stats = {}  # team_id -> {rp: 0, matches_played: 0, ...}

    for res in match_results:
        match = matches.get(res.match_id)
        if not match or match.type != MatchType.QUALIFICATION:
            continue

        # Process Red Alliance
        red_teams = [match.red1, match.red2, match.red3]
        red_score = res.get_red_score_obj()

        # Process Blue Alliance
        blue_teams = [match.blue1, match.blue2, match.blue3]
        blue_score = res.get_blue_score_obj()

        # Determine Winner RPs
        red_rp = red_score.ranking_points
        blue_rp = blue_score.ranking_points

        red_win = False
        blue_win = False
        tie = False

        if red_score.total_points > blue_score.total_points:
            red_rp += 2
            red_win = True
        elif blue_score.total_points > red_score.total_points:
            blue_rp += 2
            blue_win = True
        else:
            red_rp += 1
            blue_rp += 1
            tie = True

        # Update Stats Helper
        def update_team_stats(tid, rp, score, is_win, is_loss, is_tie):
            if tid == 0:
                return
            if tid not in team_stats:
                team_stats[tid] = {
                    "rp": 0,
                    "matches": 0,
                    "score": 0,
                    "wins": 0,
                    "losses": 0,
                    "ties": 0,
                }
            team_stats[tid]["rp"] += rp
            team_stats[tid]["matches"] += 1
            team_stats[tid]["score"] += score
            if is_win:
                team_stats[tid]["wins"] += 1
            if is_loss:
                team_stats[tid]["losses"] += 1
            if is_tie:
                team_stats[tid]["ties"] += 1

        for team_id in red_teams:
            update_team_stats(
                team_id, red_rp, red_score.total_points, red_win, blue_win, tie
            )

        for team_id in blue_teams:
            update_team_stats(
                team_id, blue_rp, blue_score.total_points, blue_win, red_win, tie
            )

    # Calculate Average RP and create Ranking objects
    ranking_objects = []
    for team_id, stats in team_stats.items():
        avg_rp = stats["rp"] / stats["matches"] if stats["matches"] > 0 else 0
        ranking_objects.append(
            Ranking(
                team_id=team_id,
                ranking_points=stats["rp"],
                matches_played=stats["matches"],
                average_rp=avg_rp,
                total_score=stats["score"],
                wins=stats["wins"],
                losses=stats["losses"],
                ties=stats["ties"],
            )
        )

    # Sort by Average RP (desc), then Total Score (desc)
    ranking_objects.sort(key=lambda x: (x.average_rp, x.total_score), reverse=True)

    # Assign Rank
    for i, rank_obj in enumerate(ranking_objects):
        rank_obj.rank = i + 1

    # Update Database
    # Clear existing rankings
    await session.execute(delete(Ranking))

    # Insert new rankings
    session.add_all(ranking_objects)
    await session.commit()

    return ranking_objects
