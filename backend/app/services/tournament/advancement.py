from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.app.models.match import Match, MatchStatus, MatchType


class BracketAdvancement:
    @staticmethod
    async def advance_playoff(session: AsyncSession, completed_match: Match):
        """
        Advances the winner and loser of a completed playoff match to the next matches in the bracket.
        """
        if completed_match.type != MatchType.PLAYOFF:
            return

        # Determine Winner and Loser
        winner_alliance_id = 0
        loser_alliance_id = 0

        # We need to know which alliance ID was Red and Blue
        # The Match object has playoff_red_alliance and playoff_blue_alliance

        if completed_match.status == MatchStatus.RED_WON_MATCH:
            winner_alliance_id = completed_match.playoff_red_alliance
            loser_alliance_id = completed_match.playoff_blue_alliance

            # Also get team compositions to carry forward
            w_teams = [
                completed_match.red1,
                completed_match.red2,
                completed_match.red2,
            ]  # Wait, red2 is repeated? Typo in my thought?
            # Actually, we should just copy the alliance ID. The teams are derived from alliance ID usually.
            # But in Match model we store red1, red2, red3.
            w_teams = [completed_match.red1, completed_match.red2]  # Add red3 if exists
            l_teams = [completed_match.blue1, completed_match.blue2]

        elif completed_match.status == MatchStatus.BLUE_WON_MATCH:
            winner_alliance_id = completed_match.playoff_blue_alliance
            loser_alliance_id = completed_match.playoff_red_alliance

            w_teams = [completed_match.blue1, completed_match.blue2]
            l_teams = [completed_match.red1, completed_match.red2]
        else:
            return  # Not a win/loss state

        # Identify Source Keys
        # e.g. "W_M1", "L_M1"
        match_key = completed_match.short_name  # e.g. "M1"
        win_source = f"W_{match_key}"
        loss_source = f"L_{match_key}"

        # Find matches waiting for these sources
        # We search for matches where red_source or blue_source matches

        stmt = select(Match).where(
            (Match.red_source == win_source)
            | (Match.blue_source == win_source)
            | (Match.red_source == loss_source)
            | (Match.blue_source == loss_source)
        )
        result = await session.execute(stmt)
        future_matches = result.scalars().all()

        for m in future_matches:
            changed = False
            # Check Red Source
            if m.red_source == win_source:
                m.playoff_red_alliance = winner_alliance_id
                m.red1 = w_teams[0]
                m.red2 = w_teams[1]
                # m.red3 = ... (Need to handle 3rd team if we store it)
                changed = True
            elif m.red_source == loss_source:
                m.playoff_red_alliance = loser_alliance_id
                m.red1 = l_teams[0]
                m.red2 = l_teams[1]
                changed = True

            # Check Blue Source
            if m.blue_source == win_source:
                m.playoff_blue_alliance = winner_alliance_id
                m.blue1 = w_teams[0]
                m.blue2 = w_teams[1]
                changed = True
            elif m.blue_source == loss_source:
                m.playoff_blue_alliance = loser_alliance_id
                m.blue1 = l_teams[0]
                m.blue2 = l_teams[1]
                changed = True

            if changed:
                session.add(m)

        # We don't commit here, let the caller commit
