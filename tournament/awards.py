import models


def create_or_update_lower_third(
    lower_third: models.LowerThird, existing_lower_thirds: list[models.LowerThird], index: int
):
    if index < len(existing_lower_thirds):
        lower_third.id = existing_lower_thirds[index].id
        lower_third.display_order = existing_lower_thirds[index].display_order
        return models.update_lower_third(lower_third)
    else:
        lower_third.display_order = models.read_next_lower_third_display_order()
        return models.create_lower_third(lower_third)


def create_or_update_award(award: models.Award, create_intro_lower_third: bool = False):
    if award.award_name == '':
        raise ValueError('Award name cannot be empty')

    team = None
    if award.team_id > 0:
        team = models.read_team_by_id(award.team_id)
        if team is None:
            raise ValueError(f'Team {award.team_id} does not exist')

    if award.id is None:
        award = models.create_award(award)
    else:
        award = models.update_award(award)

    award_intro_lower_third = models.LowerThird(top_text=award.award_name, award_id=award.id)
    award_winner_lower_third = models.LowerThird(
        top_text=award.award_name, bottom_text=award.person_name, award_id=award.id
    )

    if team is not None:
        if award.person_name == '':
            award_winner_lower_third.bottom_text = f'Team {team.id}, {team.nickname}'
        else:
            award_winner_lower_third.bottom_text = (
                f'{award.person_name} - Team {team.id}, {team.nickname}'
            )

    if award_winner_lower_third.bottom_text == '':
        award_winner_lower_third.bottom_text = 'Not assigned yet'

    lower_thirds = models.read_lower_third_by_award_id(award.id)
    bottom_index = 0
    if create_intro_lower_third:
        create_or_update_lower_third(award_intro_lower_third, lower_thirds, 0)
        bottom_index += 1

    create_or_update_lower_third(award_winner_lower_third, lower_thirds, bottom_index)
    return award


def delete_award(award_id: int):
    models.delete_award(award_id)

    lower_thirds = models.read_lower_third_by_award_id(award_id)
    for lower_third in lower_thirds:
        models.delete_lower_third(lower_third.id)


def create_or_update_winner_and_finalist_awards(winner_alliance_id: int, finalist_alliance_id: int):
    winner_alliance = models.read_alliance_by_id(winner_alliance_id)
    finalist_alliance = models.read_alliance_by_id(finalist_alliance_id)

    if winner_alliance is None or finalist_alliance is None:
        raise ValueError(
            f'Alliance {winner_alliance_id} and/or {finalist_alliance_id} does not exist'
        )

    if len(winner_alliance.team_ids) == 0 or len(finalist_alliance.team_ids) == 0:
        raise ValueError(
            f'Alliance {winner_alliance_id} and/or {finalist_alliance_id} must have at least one team'
        )

    winner_awards = models.read_awards_by_type(models.AwardType.winner_award)
    finalist_awards = models.read_awards_by_type(models.AwardType.finalist_award)

    for award in winner_awards + finalist_awards:
        delete_award(award.id)

    finalist_award = models.Award(
        award_name='Finalist',
        type=models.AwardType.finalist_award,
        team_id=finalist_alliance.team_ids[0],
    )
    create_or_update_award(finalist_award, create_intro_lower_third=True)
    for team_id in finalist_alliance.team_ids[1:]:
        finalist_award = models.Award(
            award_name='Finalist',
            type=models.AwardType.finalist_award,
            team_id=team_id,
        )
        create_or_update_award(finalist_award)

    winner_award = models.Award(
        award_name='Winner',
        type=models.AwardType.winner_award,
        team_id=winner_alliance.team_ids[0],
    )
    create_or_update_award(winner_award, create_intro_lower_third=True)
    for team_id in winner_alliance.team_ids[1:]:
        winner_award = models.Award(
            award_name='Winner',
            type=models.AwardType.winner_award,
            team_id=team_id,
        )
        create_or_update_award(winner_award)
