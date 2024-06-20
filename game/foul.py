from pydantic import BaseModel
from .rule import Rule, get_rule_by_id

class Foul(BaseModel):
    is_technical: bool = False
    team_id: int = 0
    rule_id: int = 0

    def point_value(self) -> int:
        return 5 if self.is_technical else 2
    
    def rule(self) -> Rule:
        return get_rule_by_id(self.rule_id)