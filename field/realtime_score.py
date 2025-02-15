from pydantic import BaseModel

import game


class RealtimeScore(BaseModel):
    current_score: game.Score = game.Score()
    cards: dict[str, str] = {}
    fouls_commited: bool = False
