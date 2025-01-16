import game
import models


def calculate_rankings(preserve_previous_rank: bool = False):
    matches = models.read_matches_by_type(models.MatchType.QUALIFICATION, False)
    if not matches:
        return

    rankings = {}
    for match in matches:
        if not match.is_complete():
            continue

        match_result = models.read_match_result_for_match(match.id)
        if match_result is None:
            continue

        if not match.red1_is_surrogate:
            add_match_result_to_rankings(rankings, match.red1, match_result, True)
        if not match.red2_is_surrogate:
            add_match_result_to_rankings(rankings, match.red2, match_result, True)
        if not match.red3_is_surrogate:
            add_match_result_to_rankings(rankings, match.red3, match_result, True)
        if not match.blue1_is_surrogate:
            add_match_result_to_rankings(rankings, match.blue1, match_result, False)
        if not match.blue2_is_surrogate:
            add_match_result_to_rankings(rankings, match.blue2, match_result, False)
        if not match.blue3_is_surrogate:
            add_match_result_to_rankings(rankings, match.blue3, match_result, False)

    old_rankings = models.read_all_rankings()
    old_rankings_dict = {ranking.team_id: ranking for ranking in old_rankings}

    sorted_rankings = sort_rankings(rankings)
    for i, ranking in enumerate(sorted_rankings):
        ranking.rank = i + 1
        old_ranking = old_rankings_dict.get(ranking.team_id)
        if old_ranking is not None:
            if preserve_previous_rank:
                sorted_rankings[i].previous_rank = old_ranking.previous_rank
            else:
                sorted_rankings[i].previous_rank = old_ranking.rank

    models.replace_all_rankings(sorted_rankings)
    return sorted_rankings


def calculate_team_cards(match_type: models.MatchType):
    teams = models.read_all_teams()
    for team in teams:
        team.yellow_card = False
    teams_dict = {team.id: team for team in teams}

    matches = models.read_matches_by_type(match_type, False)
    for match in matches:
        if not match.is_complete():
            continue

        match_result = models.read_match_result_for_match(match.id)
        if match_result is None:
            raise ValueError(f'Match {match.id} is complete but has no match result')

        for team_id, card in match_result.red_cards.items():
            team = teams_dict.get(team_id)
            if team is not None and (card == 'red' or card == 'dq'):
                team.yellow_card = True
                teams_dict[team_id] = team

        for team_id, card in match_result.blue_cards.items():
            team = teams_dict.get(team_id)
            if team is not None and (card == 'red' or card == 'dq'):
                team.yellow_card = True
                teams_dict[team_id] = team

    for team in teams_dict.values():
        models.update_team(team)


def add_match_result_to_rankings(
    rankings: dict[int, game.Ranking], team_id: int, match_result: models.MatchResult, is_red: bool
):
    ranking = rankings.get(team_id)
    if ranking is None:
        ranking = game.Ranking(team_id=team_id)
        rankings[team_id] = ranking

    cards = {}
    if is_red:
        cards = match_result.red_cards
    else:
        cards = match_result.blue_cards

    disqualified = False
    card = cards.get(team_id)
    if card is not None and (card == 'red' or card == 'dq'):
        disqualified = True

    if is_red:
        ranking.fields.add_score_summary(
            match_result.red_score_summary(), match_result.blue_score_summary(), disqualified
        )
    else:
        ranking.fields.add_score_summary(
            match_result.blue_score_summary(), match_result.red_score_summary(), disqualified
        )


def sort_rankings(rankings: dict[int, game.Ranking]):
    sorted_rankings = list(rankings.values())
    sorted_rankings.sort()
    return sorted_rankings
