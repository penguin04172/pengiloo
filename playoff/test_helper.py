from datetime import datetime, timedelta

import models


def assertMatchSpecsEqual(self, match_specs, expected_match_specs):
    self.assertEqual(
        len(match_specs),
        len(expected_match_specs),
        f'Length mismatch: {len(match_specs)} != {len(expected_match_specs)}',
    )
    for i, match_spec in enumerate(match_specs):
        self.assertEqual(
            match_spec.long_name,
            expected_match_specs[i].long_name,
            f'long_name mismatch at index {i}: {match_spec.long_name} != {expected_match_specs[i].long_name}',
        )
        self.assertEqual(
            match_spec.short_name,
            expected_match_specs[i].short_name,
            f'short_name mismatch at index {i}: {match_spec.short_name} != {expected_match_specs[i].short_name}',
        )
        self.assertEqual(
            match_spec.order,
            expected_match_specs[i].order,
            f'order mismatch at index {i}: {match_spec.order} != {expected_match_specs[i].order}',
        )
        self.assertEqual(
            match_spec.name_detail,
            expected_match_specs[i].name_detail,
            f'name_detail mismatch at index {i}: {match_spec.name_detail} != {expected_match_specs[i].name_detail}',
        )
        self.assertEqual(
            match_spec.match_group_id,
            expected_match_specs[i].match_group_id,
            f'match_group_id mismatch at index {i}: {match_spec.match_group_id} != {expected_match_specs[i].match_group_id}',
        )
        self.assertEqual(
            match_spec.use_tiebreak_criteria,
            expected_match_specs[i].use_tiebreak_criteria,
            f'use_tiebreak_criteria mismatch at index {i}: {match_spec.use_tiebreak_criteria} != {expected_match_specs[i].use_tiebreak_criteria}',
        )
        self.assertEqual(
            match_spec.is_hidden,
            expected_match_specs[i].is_hidden,
            f'is_hidden mismatch at index {i}: {match_spec.is_hidden} != {expected_match_specs[i].is_hidden}',
        )
        self.assertEqual(
            match_spec.tba_match_key,
            expected_match_specs[i].tba_match_key,
            f'tba_match_key mismatch at index {i}: {match_spec.tba_match_key} != {expected_match_specs[i].tba_match_key}',
        )
        self.assertEqual(
            match_spec.red_alliance_id,
            expected_match_specs[i].red_alliance_id,
            f'red_alliance_id mismatch at index {i}: {match_spec.red_alliance_id} != {expected_match_specs[i].red_alliance_id}',
        )
        self.assertEqual(
            match_spec.blue_alliance_id,
            expected_match_specs[i].blue_alliance_id,
            f'blue_alliance_id mismatch at index {i}: {match_spec.blue_alliance_id} != {expected_match_specs[i].blue_alliance_id}',
        )


class ExpectedAlliance:
    def __init__(self, red_alliance_id, blue_alliance_id):
        self.red_alliance_id = red_alliance_id
        self.blue_alliance_id = blue_alliance_id


def assertMatchSpecAlliances(self, match_specs, expected_alliances):
    self.assertEqual(len(match_specs), len(expected_alliances))
    for i, match_spec in enumerate(match_specs):
        self.assertEqual(match_spec.red_alliance_id, expected_alliances[i].red_alliance_id)
        self.assertEqual(match_spec.blue_alliance_id, expected_alliances[i].blue_alliance_id)


def assertMatchGroups(self, match_groups, expected_match_groups_ids):
    self.assertEqual(len(match_groups), len(expected_match_groups_ids))
    self.assertEqual(
        set(match_groups.keys()),
        set(expected_match_groups_ids),
        f'Match groups keys mismatch: {set(match_groups.keys())} != {set(expected_match_groups_ids)}',
    )


def assertMatchOutcome(self, match_group, red_destination, blue_destination):
    self.assertEqual(match_group.red_alliance_destination(), red_destination)
    self.assertEqual(match_group.blue_alliance_destination(), blue_destination)


def create_test_alliance(allianceCount: int):
    for i in range(1, allianceCount + 1):
        alliance = models.Alliance(
            id=i,
            team_ids=[100 * i + 1, 100 * i + 2, 100 * i + 3, 100 * i + 4],
            line_up=[100 * i + 2, 100 * i + 1, 100 * i + 3],
        )
        alliance = models.create_alliance(alliance)


def assert_match(
    self,
    match,
    type_order,
    time_in_sec,
    long_name,
    short_name,
    name_detail,
    match_group_id,
    red_alliance,
    blue_alliance,
    use_tiebreak_criteria,
    tba_comp_level,
    tba_set_number,
    tba_match_number,
):
    self.assertEqual(match.type, models.MatchType.PLAYOFF)
    self.assertEqual(match.type_order, type_order)
    self.assertEqual(match.scheduled_time, datetime.fromtimestamp(time_in_sec))
    self.assertEqual(match.long_name, long_name)
    self.assertEqual(match.short_name, short_name)
    self.assertEqual(match.name_detail, name_detail)
    self.assertEqual(match.playoff_match_group_id, match_group_id)
    self.assertEqual(match.playoff_red_alliance, red_alliance)
    self.assertEqual(match.playoff_blue_alliance, blue_alliance)
    if red_alliance == 0:
        self.assertEqual(match.red1, 0)
        self.assertEqual(match.red2, 0)
        self.assertEqual(match.red3, 0)
    else:
        self.assertEqual(match.red1, 100 * red_alliance + 2)
        self.assertEqual(match.red2, 100 * red_alliance + 1)
        self.assertEqual(match.red3, 100 * red_alliance + 3)

    if blue_alliance == 0:
        self.assertEqual(match.blue1, 0)
        self.assertEqual(match.blue2, 0)
        self.assertEqual(match.blue3, 0)
    else:
        self.assertEqual(match.blue1, 100 * blue_alliance + 2)
        self.assertEqual(match.blue2, 100 * blue_alliance + 1)
        self.assertEqual(match.blue3, 100 * blue_alliance + 3)

    self.assertEqual(match.use_tiebreak_criteria, use_tiebreak_criteria)
    self.assertEqual(match.tba_match_key.comp_level, tba_comp_level)
    self.assertEqual(match.tba_match_key.set_number, tba_set_number)
    self.assertEqual(match.tba_match_key.match_number, tba_match_number)


def assert_break(self, scheduled_break, type_order_before, time_sec, duration_sec, description):
    self.assertEqual(scheduled_break.match_type, models.MatchType.PLAYOFF)
    self.assertEqual(scheduled_break.type_order_before, type_order_before)
    self.assertEqual(scheduled_break.time, datetime.fromtimestamp(time_sec))
    self.assertEqual(scheduled_break.duration_sec, duration_sec)
    self.assertEqual(scheduled_break.description, description)
