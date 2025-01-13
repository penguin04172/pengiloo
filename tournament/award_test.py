import unittest

import models
from models.base import db

from .awards import (
    create_or_update_award,
    create_or_update_winner_and_finalist_awards,
    delete_award,
)


class AwardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        db.bind(provider='sqlite', filename=':memory:', create_db=True)
        db.generate_mapping(create_tables=True)

    @classmethod
    def tearDownClass(cls) -> None:
        db.disconnect()

    def setUp(self) -> None:
        db.create_tables(True)

    def tearDown(self) -> None:
        db.drop_all_tables(with_all_data=True)

    def test_create_or_update_award_with_intro(self):
        models.create_team(models.Team(id=1234, nickname='Test Team'))

        award = models.Award(
            type=models.AwardType.judged_award,
            award_name='Test Award',
            team_id=0,
            person_name='',
        )
        award = create_or_update_award(award, create_intro_lower_third=True)

        award2 = models.read_award_by_id(award.id)
        self.assertEqual(award2.id, award.id)
        lower_thirds = models.read_all_lower_thirds()
        self.assertEqual(len(lower_thirds), 2)
        self.assertEqual(lower_thirds[0].top_text, 'Test Award')
        self.assertEqual(lower_thirds[0].bottom_text, '')
        self.assertEqual(lower_thirds[1].top_text, 'Test Award')
        self.assertEqual(lower_thirds[1].bottom_text, 'Not assigned yet')

        award.award_name = 'Test Award 2'
        award.team_id = 1234
        award = create_or_update_award(award, create_intro_lower_third=True)
        award2 = models.read_award_by_id(award.id)
        self.assertEqual(award2.id, award.id)
        lower_thirds = models.read_all_lower_thirds()
        self.assertEqual(len(lower_thirds), 2)
        self.assertEqual(lower_thirds[0].top_text, 'Test Award 2')
        self.assertEqual(lower_thirds[0].bottom_text, '')
        self.assertEqual(lower_thirds[1].top_text, 'Test Award 2')
        self.assertEqual(lower_thirds[1].bottom_text, 'Team 1234, Test Team')

        delete_award(award.id)
        award2 = models.read_award_by_id(award.id)
        self.assertIsNone(award2)
        lower_thirds = models.read_all_lower_thirds()
        self.assertEqual(len(lower_thirds), 0)

    def test_create_or_update_award_without_intro(self):
        models.create_team(models.Team(id=1234, nickname='Test Team'))
        other_lower_third = models.LowerThird(top_text='Macro', bottom_text='Polo')
        other_lower_third = models.create_lower_third(other_lower_third)

        award = models.Award(
            type=models.AwardType.winner_award,
            award_name='Winner',
            team_id=0,
            person_name='Pengu',
        )
        award = create_or_update_award(award, create_intro_lower_third=False)

        award2 = models.read_award_by_id(award.id)
        self.assertEqual(award2.id, award.id)
        lower_thirds = models.read_all_lower_thirds()
        self.assertEqual(len(lower_thirds), 2)
        self.assertEqual(lower_thirds[0], other_lower_third)
        self.assertEqual(lower_thirds[1].top_text, 'Winner')
        self.assertEqual(lower_thirds[1].bottom_text, 'Pengu')

        award.team_id = 1234
        award = create_or_update_award(award, create_intro_lower_third=False)
        award2 = models.read_award_by_id(award.id)
        self.assertEqual(award2.id, award.id)
        lower_thirds = models.read_all_lower_thirds()
        self.assertEqual(len(lower_thirds), 2)
        self.assertEqual(lower_thirds[0], other_lower_third)
        self.assertEqual(lower_thirds[1].top_text, 'Winner')
        self.assertEqual(lower_thirds[1].bottom_text, 'Pengu - Team 1234, Test Team')

        delete_award(award.id)
        award2 = models.read_award_by_id(award.id)
        self.assertIsNone(award2)
        lower_thirds = models.read_all_lower_thirds()
        self.assertEqual(len(lower_thirds), 1)
        self.assertEqual(lower_thirds[0], other_lower_third)

    def test_create_or_update_winner_and_finalist_awards(self):
        models.create_alliance(
            models.Alliance(id=1, team_ids=[101, 102, 103, 104], line_up=[102, 101, 103])
        )
        models.create_alliance(
            models.Alliance(id=2, team_ids=[201, 202, 203, 204], line_up=[202, 201, 203])
        )
        models.create_team(models.Team(id=101))
        models.create_team(models.Team(id=102))
        models.create_team(models.Team(id=103))
        models.create_team(models.Team(id=104))
        models.create_team(models.Team(id=201))
        models.create_team(models.Team(id=202))
        models.create_team(models.Team(id=203))
        models.create_team(models.Team(id=204))

        create_or_update_winner_and_finalist_awards(2, 1)
        awards = models.read_all_awards()
        self.assertEqual(len(awards), 8)
        print(awards[0])
        # print(
        #     models.Award(
        #         id=1,
        #         type=models.AwardType.finalist_award,
        #         award_name='Finalist',
        #         team_id=101,
        #         person_name='',
        #     )
        # )
        self.assertEqual(
            awards[0],
            models.Award(
                id=1,
                type=models.AwardType.finalist_award,
                award_name='Finalist',
                team_id=101,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[1],
            models.Award(
                id=2,
                type=models.AwardType.finalist_award,
                award_name='Finalist',
                team_id=102,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[2],
            models.Award(
                id=3,
                type=models.AwardType.finalist_award,
                award_name='Finalist',
                team_id=103,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[3],
            models.Award(
                id=4,
                type=models.AwardType.finalist_award,
                award_name='Finalist',
                team_id=104,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[4],
            models.Award(
                id=5,
                type=models.AwardType.winner_award,
                award_name='Winner',
                team_id=201,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[5],
            models.Award(
                id=6,
                type=models.AwardType.winner_award,
                award_name='Winner',
                team_id=202,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[6],
            models.Award(
                id=7,
                type=models.AwardType.winner_award,
                award_name='Winner',
                team_id=203,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[7],
            models.Award(
                id=8,
                type=models.AwardType.winner_award,
                award_name='Winner',
                team_id=204,
                person_name='',
            ),
        )
        lower_thirds = models.read_all_lower_thirds()
        self.assertEqual(len(lower_thirds), 10)
        self.assertEqual(lower_thirds[0].top_text, 'Finalist')
        self.assertEqual(lower_thirds[0].bottom_text, '')
        self.assertEqual(lower_thirds[1].top_text, 'Finalist')
        self.assertEqual(lower_thirds[1].bottom_text, 'Team 101,')
        self.assertEqual(lower_thirds[5].top_text, 'Winner')
        self.assertEqual(lower_thirds[5].bottom_text, '')
        self.assertEqual(lower_thirds[6].top_text, 'Winner')
        self.assertEqual(lower_thirds[6].bottom_text, 'Team 201,')

        create_or_update_winner_and_finalist_awards(1, 2)
        awards = models.read_all_awards()
        self.assertEqual(len(awards), 8)
        self.assertEqual(
            awards[0],
            models.Award(
                id=9,
                type=models.AwardType.finalist_award,
                award_name='Finalist',
                team_id=201,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[1],
            models.Award(
                id=10,
                type=models.AwardType.finalist_award,
                award_name='Finalist',
                team_id=202,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[2],
            models.Award(
                id=11,
                type=models.AwardType.finalist_award,
                award_name='Finalist',
                team_id=203,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[3],
            models.Award(
                id=12,
                type=models.AwardType.finalist_award,
                award_name='Finalist',
                team_id=204,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[4],
            models.Award(
                id=13,
                type=models.AwardType.winner_award,
                award_name='Winner',
                team_id=101,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[5],
            models.Award(
                id=14,
                type=models.AwardType.winner_award,
                award_name='Winner',
                team_id=102,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[6],
            models.Award(
                id=15,
                type=models.AwardType.winner_award,
                award_name='Winner',
                team_id=103,
                person_name='',
            ),
        )
        self.assertEqual(
            awards[7],
            models.Award(
                id=16,
                type=models.AwardType.winner_award,
                award_name='Winner',
                team_id=104,
                person_name='',
            ),
        )
        lower_thirds = models.read_all_lower_thirds()
        self.assertEqual(len(lower_thirds), 10)
        self.assertEqual(lower_thirds[0].top_text, 'Finalist')
        self.assertEqual(lower_thirds[0].bottom_text, '')
        self.assertEqual(lower_thirds[1].top_text, 'Finalist')
        self.assertEqual(lower_thirds[1].bottom_text, 'Team 201,')
        self.assertEqual(lower_thirds[5].top_text, 'Winner')
        self.assertEqual(lower_thirds[5].bottom_text, '')
        self.assertEqual(lower_thirds[6].top_text, 'Winner')
        self.assertEqual(lower_thirds[6].bottom_text, 'Team 101,')
