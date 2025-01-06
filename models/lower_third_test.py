import unittest

from .base import db
from .lower_third import (
    LowerThird,
    create_lower_third,
    delete_lower_third,
    read_all_lower_thirds,
    read_lower_third_by_award_id,
    read_lower_third_by_id,
    read_next_lower_third_display_order,
    truncate_lower_thirds,
    update_lower_third,
)


class TeamTest(unittest.TestCase):
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

    def test_read_nonexist_lower_third(self):
        lower_third = read_lower_third_by_id(7641)
        self.assertIsNone(lower_third)

    def test_lower_third_crud(self):
        lower_third_list = read_all_lower_thirds()
        self.assertEqual(0, len(lower_third_list))

        lower_third = create_lower_third(
            LowerThird(top_text='Top Text', bottom_text='Bottom Text', display_order=1)
        )
        lower_third_2 = read_lower_third_by_id(1)
        self.assertEqual(lower_third, lower_third_2)

        lower_third.bottom_text = 'Blorpy'
        update_lower_third(lower_third)
        lower_third_2 = read_lower_third_by_id(1)
        self.assertEqual(lower_third.bottom_text, lower_third_2.bottom_text)

        lower_third_list = read_all_lower_thirds()
        self.assertEqual(1, len(lower_third_list))

        delete_lower_third(lower_third.id)
        lower_third_2 = read_lower_third_by_id(1)
        self.assertIsNone(lower_third_2)

    def test_truncate_lower_thirds(self):
        create_lower_third(
            LowerThird(top_text='Top Text', bottom_text='Bottom Text', display_order=0)
        )
        truncate_lower_thirds()
        lower_third_2 = read_lower_third_by_id(1)
        self.assertIsNone(lower_third_2)

    def test_read_lower_third_by_award_id(self):
        next_display_order = read_next_lower_third_display_order()
        self.assertEqual(1, next_display_order)
        create_lower_third(
            LowerThird(top_text='Top Text', bottom_text='Bottom Text', display_order=1)
        )
        lower_third_2 = create_lower_third(
            LowerThird(top_text='Award 1', bottom_text='', display_order=2, award_id=5)
        )
        lower_third_3 = create_lower_third(
            LowerThird(top_text='Award 2', bottom_text='', display_order=3, award_id=2)
        )
        lower_third_4 = create_lower_third(
            LowerThird(
                top_text='Award 1', bottom_text='Award 1 Winner', display_order=4, award_id=5
            )
        )
        lower_third_list = read_all_lower_thirds()
        self.assertEqual(4, len(lower_third_list))
        next_display_order = read_next_lower_third_display_order()
        self.assertEqual(5, next_display_order)

        lower_third_list = read_lower_third_by_award_id(5)
        self.assertEqual(2, len(lower_third_list))
        self.assertEqual(lower_third_2, lower_third_list[0])
        self.assertEqual(lower_third_4, lower_third_list[1])

        lower_third_list = read_lower_third_by_award_id(2)
        self.assertEqual(1, len(lower_third_list))
        self.assertEqual(lower_third_3, lower_third_list[0])

        lower_third_list = read_lower_third_by_award_id(7641)
        self.assertEqual(0, len(lower_third_list))
