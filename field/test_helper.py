import random

import game

from .arena import Arena


def setup_test_arena(self):
    random.seed(0)

    arena = Arena()
    return arena


def setup_test_arena_with_parameter(self):
    game.timing.warmup_duration_sec = 3
    game.timing.pause_duration_sec = 2
    return setup_test_arena(self)
