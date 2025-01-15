import game


class PlayoffMatchResult:
    status: game.MATCH_STATUS

    def __init__(self, status: game.MATCH_STATUS):
        self.status = status


class BreakSpec:
    order_before: int
    duration_sec: int
    description: str

    def __init__(self, order_before: int, duration_sec: int, description: str):
        self.order_before = order_before
        self.duration_sec = duration_sec
        self.description = description

    def __eq__(self, other):
        if isinstance(other, BreakSpec):
            return (
                self.order_before == other.order_before
                and self.description == other.description
                and self.duration_sec == other.duration_sec
            )
        return False

    def __repr__(self):
        return (
            f'BreakSpec(order_before={self.order_before}, '
            f"description='{self.description}', duration_sec={self.duration_sec})"
        )
