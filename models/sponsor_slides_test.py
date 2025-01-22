import unittest

from .base import db
from .sponsor_slides import (
    SponsorSlide,
    create_sponsor_slide,
    delete_sponsor_slide,
    get_next_sponsor_slide_display_order,
    read_sponsor_slide_by_id,
    truncate_sponsor_slides,
    update_sponsor_slide,
)


class TestSponsorSlides(unittest.TestCase):
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

    def test_sponsor_slide_crud(self):
        self.assertEqual(get_next_sponsor_slide_display_order(), 1)

        slide = SponsorSlide(
            subtitle='Subtitle',
            line1='Line 1',
            line2='Line 2',
            image='',
            display_time_sec=10,
            display_order=1,
        )
        slide = create_sponsor_slide(slide)

        slide2 = read_sponsor_slide_by_id(1)
        self.assertEqual(slide, slide2)
        self.assertEqual(get_next_sponsor_slide_display_order(), 2)

        slide.line1 = 'New Line 1'
        update_sponsor_slide(slide)
        slide2 = read_sponsor_slide_by_id(1)
        self.assertEqual(slide, slide2)

        delete_sponsor_slide(1)
        slide2 = read_sponsor_slide_by_id(1)
        self.assertIsNone(slide2)

    def test_truncate_sponsor_slides(self):
        slide = SponsorSlide(
            subtitle='Subtitle',
            line1='Line 1',
            line2='Line 2',
            image='',
            display_time_sec=10,
            display_order=1,
        )
        create_sponsor_slide(slide)
        truncate_sponsor_slides()

        slide2 = read_sponsor_slide_by_id(1)
        self.assertIsNone(slide2)
        self.assertEqual(get_next_sponsor_slide_display_order(), 1)
