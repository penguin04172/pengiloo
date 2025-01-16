import unittest
from datetime import timedelta

from .amp_speaker import AmpSpeaker
from .game_specific import specific

match_start_time = timedelta()


def time_after_start(sec: float) -> timedelta:
    return match_start_time + timedelta(seconds=sec)


class AmpSpeakerTest(unittest.TestCase):
    def test_calculation_methods(self):
        amp_speaker = AmpSpeaker(
            auto_amp_notes=1,
            teleop_amp_notes=2,
            auto_speaker_notes=3,
            teleop_unamplified_speaker_notes=5,
            teleop_amplified_speaker_notes=8,
        )
        self.assertEqual(3, amp_speaker.amp_notes_scored())
        self.assertEqual(16, amp_speaker.speaker_notes_scored())
        self.assertEqual(19, amp_speaker.total_notes_scored())
        self.assertEqual(17, amp_speaker.auto_note_points())
        self.assertEqual(4, amp_speaker.amp_points())
        self.assertEqual(65, amp_speaker.speaker_points())

    def test_amp_speaker_match_sequence(self):
        amp_speaker = AmpSpeaker()

        def assert_amp_speaker(
            auto_amp_notes,
            teleop_amp_notes,
            auto_speaker_notes,
            teleop_unamplified_speaker_notes,
            teleop_amplified_speaker_notes,
        ):
            self.assertEqual(auto_amp_notes, amp_speaker.auto_amp_notes)
            self.assertEqual(teleop_amp_notes, amp_speaker.teleop_amp_notes)
            self.assertEqual(auto_speaker_notes, amp_speaker.auto_speaker_notes)
            self.assertEqual(
                teleop_unamplified_speaker_notes, amp_speaker.teleop_unamplified_speaker_notes
            )
            self.assertEqual(
                teleop_amplified_speaker_notes, amp_speaker.teleop_amplified_speaker_notes
            )

        amp_speaker.update_state(0, 0, False, False, match_start_time, time_after_start(0))
        assert_amp_speaker(0, 0, 0, 0, 0)

        # Scoring during auto
        amp_speaker.update_state(1, 0, False, False, match_start_time, time_after_start(1))
        assert_amp_speaker(1, 0, 0, 0, 0)
        self.assertEqual(1, amp_speaker.banked_amp_notes)
        self.assertEqual(
            True, amp_speaker.is_coop_window_open(match_start_time, time_after_start(1))
        )

        amp_speaker.update_state(2, 0, False, False, match_start_time, time_after_start(2))
        assert_amp_speaker(2, 0, 0, 0, 0)
        self.assertEqual(2, amp_speaker.banked_amp_notes)

        amp_speaker.update_state(2, 3, False, False, match_start_time, time_after_start(3))
        assert_amp_speaker(2, 0, 3, 0, 0)

        amp_speaker.update_state(3, 4, False, False, match_start_time, time_after_start(4))
        assert_amp_speaker(3, 0, 4, 0, 0)
        self.assertEqual(2, amp_speaker.banked_amp_notes)

        # Pressing button during auto -> not effect
        amp_speaker.update_state(3, 4, True, True, match_start_time, time_after_start(5))
        assert_amp_speaker(3, 0, 4, 0, 0)
        self.assertEqual(2, amp_speaker.banked_amp_notes)
        self.assertEqual(False, amp_speaker.coop_activated)
        self.assertEqual(0, amp_speaker.amplified_time_remaining(time_after_start(5)))

        # Scoring around the grace period
        amp_speaker.update_state(4, 6, False, False, match_start_time, time_after_start(17.9))
        assert_amp_speaker(4, 0, 6, 0, 0)

        amp_speaker.update_state(5, 8, False, False, match_start_time, time_after_start(18.1))
        assert_amp_speaker(4, 1, 6, 2, 0)
        self.assertEqual(2, amp_speaker.banked_amp_notes)

        # Activate coop
        amp_speaker.update_state(5, 8, False, True, match_start_time, time_after_start(20))
        assert_amp_speaker(4, 1, 6, 2, 0)
        self.assertEqual(1, amp_speaker.banked_amp_notes)
        self.assertEqual(True, amp_speaker.coop_activated)

        # Activate coop twice
        amp_speaker.update_state(5, 8, False, False, match_start_time, time_after_start(21))
        assert_amp_speaker(4, 1, 6, 2, 0)
        self.assertEqual(1, amp_speaker.banked_amp_notes)
        self.assertEqual(True, amp_speaker.coop_activated)

        # Activate amplify with insufficient notes banked
        amp_speaker.update_state(5, 8, True, False, match_start_time, time_after_start(22))
        assert_amp_speaker(4, 1, 6, 2, 0)
        self.assertEqual(1, amp_speaker.banked_amp_notes)
        self.assertEqual(False, amp_speaker.is_amplified(time_after_start(22), False))

        # Scoring during teleop
        amp_speaker.update_state(7, 8, False, False, match_start_time, time_after_start(23))
        assert_amp_speaker(4, 3, 6, 2, 0)
        self.assertEqual(2, amp_speaker.banked_amp_notes)

        amp_speaker.update_state(7, 8, True, False, match_start_time, time_after_start(24))
        assert_amp_speaker(4, 3, 6, 2, 0)
        self.assertEqual(0, amp_speaker.banked_amp_notes)
        self.assertEqual(True, amp_speaker.is_amplified(time_after_start(24.1), False))
        self.assertEqual(9.9, amp_speaker.amplified_time_remaining(time_after_start(24.1)))

        # Scoring Amplified Speaker and Amp
        amp_speaker.update_state(8, 11, False, False, match_start_time, time_after_start(25))
        assert_amp_speaker(4, 4, 6, 2, 3)
        self.assertEqual(0, amp_speaker.banked_amp_notes)
        self.assertEqual(True, amp_speaker.is_amplified(time_after_start(26), False))
        self.assertEqual(8, amp_speaker.amplified_time_remaining(time_after_start(26)))

        # Note limit for amplified speaker
        amp_speaker.update_state(8, 15, False, False, match_start_time, time_after_start(27))
        assert_amp_speaker(4, 4, 6, 5, 4)
        self.assertEqual(0, amp_speaker.banked_amp_notes)
        self.assertEqual(False, amp_speaker.is_amplified(time_after_start(27), False))
        self.assertEqual(0, amp_speaker.amplified_time_remaining(time_after_start(27)))

        # Another amplified cycle for grace period
        amp_speaker.update_state(10, 15, True, False, match_start_time, time_after_start(30))
        assert_amp_speaker(4, 6, 6, 5, 4)
        self.assertEqual(0, amp_speaker.banked_amp_notes)
        self.assertEqual(True, amp_speaker.is_amplified(time_after_start(31), False))
        self.assertEqual(9, amp_speaker.amplified_time_remaining(time_after_start(31)))

        amp_speaker.update_state(10, 16, True, False, match_start_time, time_after_start(32))
        assert_amp_speaker(4, 6, 6, 5, 5)

        amp_speaker.update_state(10, 17, False, False, match_start_time, time_after_start(42.9))
        assert_amp_speaker(4, 6, 6, 5, 6)
        self.assertEqual(True, amp_speaker.is_amplified(time_after_start(42.9), True))
        self.assertEqual(False, amp_speaker.is_amplified(time_after_start(42.9), False))
        self.assertEqual(0, amp_speaker.amplified_time_remaining(time_after_start(42.9)))

        amp_speaker.update_state(10, 18, True, False, match_start_time, time_after_start(43.1))
        assert_amp_speaker(4, 6, 6, 6, 6)
        self.assertEqual(False, amp_speaker.is_amplified(time_after_start(43.1), True))

        # Test endmatch with grace period
        amp_speaker.update_state(11, 21, False, False, match_start_time, time_after_start(152.9))
        assert_amp_speaker(4, 7, 6, 9, 6)
        self.assertEqual(1, amp_speaker.banked_amp_notes)

        amp_speaker.update_state(13, 23, True, False, match_start_time, time_after_start(153.1))
        assert_amp_speaker(4, 7, 6, 11, 6)
        self.assertEqual(1, amp_speaker.banked_amp_notes)

        amp_speaker.update_state(13, 24, True, False, match_start_time, time_after_start(157.9))
        assert_amp_speaker(4, 7, 6, 12, 6)

        amp_speaker.update_state(13, 25, False, False, match_start_time, time_after_start(158.1))
        assert_amp_speaker(4, 7, 6, 12, 6)

        # Reset amp_speaker
        amp_speaker = AmpSpeaker()
        assert_amp_speaker(0, 0, 0, 0, 0)
        self.assertEqual(0, amp_speaker.banked_amp_notes)

        # Activate coop with insufficient note banked
        amp_speaker.update_state(0, 0, False, True, match_start_time, time_after_start(20))
        self.assertEqual(False, amp_speaker.coop_activated)

        # Activate coop with closing window
        self.assertEqual(
            True, amp_speaker.is_coop_window_open(match_start_time, time_after_start(62.9))
        )
        amp_speaker.update_state(1, 0, False, True, match_start_time, time_after_start(62.9))
        assert_amp_speaker(0, 1, 0, 0, 0)
        self.assertEqual(0, amp_speaker.banked_amp_notes)
        self.assertEqual(True, amp_speaker.coop_activated)
        self.assertEqual(
            True, amp_speaker.is_coop_window_open(match_start_time, time_after_start(62.9))
        )

        # Undo coop and try to activate coop with closed window
        amp_speaker = AmpSpeaker()
        assert_amp_speaker(0, 0, 0, 0, 0)
        self.assertEqual(
            False, amp_speaker.is_coop_window_open(match_start_time, time_after_start(63.1))
        )

        amp_speaker.update_state(1, 0, False, True, match_start_time, time_after_start(63.1))
        assert_amp_speaker(0, 1, 0, 0, 0)
        self.assertEqual(1, amp_speaker.banked_amp_notes)
        self.assertEqual(False, amp_speaker.coop_activated)

        # Backtrack and disable coop
        assert_amp_speaker(0, 1, 0, 0, 0)
        self.assertEqual(1, amp_speaker.banked_amp_notes)
        self.assertEqual(
            True, amp_speaker.is_coop_window_open(match_start_time, time_after_start(60))
        )
        specific.melody_bonus_threshold_with_coop = 0
        self.assertEqual(
            False, amp_speaker.is_coop_window_open(match_start_time, time_after_start(60))
        )

        amp_speaker.update_state(2, 0, False, True, match_start_time, time_after_start(60))
        assert_amp_speaker(0, 2, 0, 0, 0)
        self.assertEqual(2, amp_speaker.banked_amp_notes)
        self.assertEqual(False, amp_speaker.coop_activated)

        # Test with different amplification note limit and duration
        specific.amplification_note_limit = 3
        specific.amplification_duration_sec = 6

        amp_speaker.update_state(2, 0, True, False, match_start_time, time_after_start(70))
        assert_amp_speaker(0, 2, 0, 0, 0)

        amp_speaker.update_state(2, 1, True, False, match_start_time, time_after_start(71))
        assert_amp_speaker(0, 2, 0, 0, 1)
        self.assertEqual(True, amp_speaker.is_amplified(time_after_start(71), False))
        self.assertEqual(5, amp_speaker.amplified_time_remaining(time_after_start(71)))

        amp_speaker.update_state(2, 4, False, False, match_start_time, time_after_start(72))
        assert_amp_speaker(0, 2, 0, 1, 3)
        self.assertEqual(False, amp_speaker.is_amplified(time_after_start(72), True))
        self.assertEqual(0, amp_speaker.amplified_time_remaining(time_after_start(72)))

        # Test with no amplification note limit with longer duration
        specific.amplification_note_limit = 0
        specific.amplification_duration_sec = 23
        amp_speaker.last_amplified_time = timedelta()
        amp_speaker.update_state(4, 4, True, False, match_start_time, time_after_start(73))
        assert_amp_speaker(0, 4, 0, 1, 3)
        self.assertEqual(0, amp_speaker.banked_amp_notes)
        self.assertEqual(True, amp_speaker.is_amplified(time_after_start(74), True))
        self.assertEqual(22, amp_speaker.amplified_time_remaining(time_after_start(74)))

        amp_speaker.update_state(100, 44, False, False, match_start_time, time_after_start(94))
        assert_amp_speaker(0, 100, 0, 1, 43)
        self.assertEqual(0, amp_speaker.banked_amp_notes)
        self.assertEqual(True, amp_speaker.is_amplified(time_after_start(94), False))
        self.assertEqual(2, amp_speaker.amplified_time_remaining(time_after_start(94)))

        amp_speaker.update_state(101, 57, False, False, match_start_time, time_after_start(98.9))
        assert_amp_speaker(0, 101, 0, 1, 56)
        self.assertEqual(1, amp_speaker.banked_amp_notes)
        self.assertEqual(True, amp_speaker.is_amplified(time_after_start(98.9), True))
        self.assertLess(amp_speaker.amplified_time_remaining(time_after_start(98.9)), 0.2)

        amp_speaker.update_state(102, 60, False, False, match_start_time, time_after_start(99.1))
        assert_amp_speaker(0, 102, 0, 4, 56)
        self.assertEqual(2, amp_speaker.banked_amp_notes)
        self.assertEqual(False, amp_speaker.is_amplified(time_after_start(99.1), True))
        self.assertEqual(0, amp_speaker.amplified_time_remaining(time_after_start(99.1)))

        # Restore default
        specific.amplification_note_limit = 4
        specific.amplification_duration_sec = 10

        # Test amplification before endmatch
        amp_speaker.update_state(102, 60, True, False, match_start_time, time_after_start(152))
        amp_speaker.update_state(102, 63, True, False, match_start_time, time_after_start(157))
        assert_amp_speaker(0, 102, 0, 4, 59)
        self.assertEqual(True, amp_speaker.is_amplified(time_after_start(157), True))
        self.assertEqual(5, amp_speaker.amplified_time_remaining(time_after_start(157)))

        amp_speaker.update_state(102, 66, True, False, match_start_time, time_after_start(157.9))
        assert_amp_speaker(0, 102, 0, 6, 60)
