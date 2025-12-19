import secrets
from collections import defaultdict
from typing import List
from datetime import timedelta
from backend.app.models.match import Match, MatchType, MatchStatus


class Scheduler:
    def __init__(self, team_ids: List[int], teams_per_alliance: int = 3):
        self.team_ids = team_ids
        self.teams_per_alliance = teams_per_alliance
        self.rng = secrets.SystemRandom()

        # Stats
        self.matches_played = defaultdict(int)
        self.red_played = defaultdict(int)
        self.blue_played = defaultdict(int)
        self.consecutive_streak = defaultdict(int)
        self.last_match_idx = defaultdict(lambda: -1)

    def assign_times(self, matches: List[Match], blocks: List):
        """
        Assigns scheduled_time to matches based on available ScheduleBlocks.
        blocks: List[ScheduleBlock]
        """
        # Sort blocks by start time
        sorted_blocks = sorted(blocks, key=lambda b: b.start_time)

        match_idx = 0
        total_matches = len(matches)

        for block in sorted_blocks:
            current_time = block.start_time

            while match_idx < total_matches:
                # Check if next match fits
                if (
                    current_time + timedelta(seconds=block.match_interval_sec)
                    > block.end_time
                ):
                    break  # Block full

                match = matches[match_idx]

                # Check type match
                if match.type == block.type:
                    match.scheduled_time = current_time
                    current_time += timedelta(seconds=block.match_interval_sec)
                    match_idx += 1
                else:
                    # Skip matches that don't match the block type?
                    # For now, assume we only pass matches of the correct type or we stop.
                    # If we have mixed matches, we should probably filter before calling.
                    break

    def generate(self, total_matches: int) -> List[Match]:
        schedule = []

        for match_idx in range(total_matches):
            # 1. Filter eligible teams
            candidates = []
            for team in self.team_ids:
                # Constraint: Cannot play continuously > 3 matches
                # If played in last match, check streak
                if self.last_match_idx[team] == match_idx - 1:
                    if self.consecutive_streak[team] >= 3:
                        continue  # Skip this team

                candidates.append(team)

            # 2. Select 2*N teams
            needed = self.teams_per_alliance * 2

            # Heuristic: Prioritize teams with fewest matches played
            # Group by matches_played
            by_played = defaultdict(list)
            for team in candidates:
                by_played[self.matches_played[team]].append(team)

            selected_teams = []

            # Iterate from lowest played count upwards
            sorted_counts = sorted(by_played.keys())
            for count in sorted_counts:
                group = by_played[count]
                self.rng.shuffle(group)  # True Random Shuffle

                take = min(len(group), needed - len(selected_teams))
                selected_teams.extend(group[:take])

                if len(selected_teams) == needed:
                    break

            if len(selected_teams) < needed:
                raise Exception(
                    f"Cannot generate valid schedule at match {match_idx + 1}. Not enough eligible teams ({len(selected_teams)}/{needed}). Try reducing matches or increasing teams."
                )

            # 3. Assign Sides (Red/Blue Balance)
            # Sort by (Red - Blue) ascending.
            # Lower value => Played less Red (or more Blue) => Needs Red.
            # Higher value => Played more Red => Needs Blue.
            # Add jitter to break ties randomly
            selected_teams.sort(
                key=lambda t: (self.red_played[t] - self.blue_played[t])
                + self.rng.uniform(-0.4, 0.4)
            )

            red_alliance = selected_teams[: self.teams_per_alliance]
            blue_alliance = selected_teams[self.teams_per_alliance :]

            # 4. Create Match Object
            match = Match(
                type=MatchType.QUALIFICATION,
                type_order=match_idx + 1,
                short_name=f"Q{match_idx + 1}",
                long_name=f"Qualification {match_idx + 1}",
                status=MatchStatus.PRE_MATCH,
                red1=red_alliance[0],
                red2=red_alliance[1] if len(red_alliance) > 1 else 0,
                red3=red_alliance[2] if len(red_alliance) > 2 else 0,
                blue1=blue_alliance[0],
                blue2=blue_alliance[1] if len(blue_alliance) > 1 else 0,
                blue3=blue_alliance[2] if len(blue_alliance) > 2 else 0,
            )
            schedule.append(match)

            # 5. Update Stats
            for team in selected_teams:
                self.matches_played[team] += 1
                if self.last_match_idx[team] == match_idx - 1:
                    self.consecutive_streak[team] += 1
                else:
                    self.consecutive_streak[team] = 1
                self.last_match_idx[team] = match_idx

            for team in red_alliance:
                self.red_played[team] += 1
            for team in blue_alliance:
                self.blue_played[team] += 1

        return schedule
