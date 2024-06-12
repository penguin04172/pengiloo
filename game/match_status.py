from enum import Enum

class MATCH_STATUS(Enum):
    match_scheduled = 0
    match_hidden = 1
    red_won_match = 2
    blue_won_match = 3
    tie_match = 4
