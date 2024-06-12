from pydantic import BaseModel

class GameSpecific(BaseModel):
    melody_bouns_threshold_without_coop: int = 18
    melody_bonus_threshold_with_coop: int = 15
    amplification_note_limit: int = 4
    amplification_duration_sec: int = 10

game_specific = GameSpecific()

