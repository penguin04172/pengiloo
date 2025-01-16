from fastapi import WebSocket


class ScoringPanelRegister:
    scoring_panels: dict[str, dict[WebSocket, bool]]

    def __init__(self):
        self.scoring_panels = {'red': {}, 'blue': {}}

    def reset_score_commited(self):
        for alliance_panels in self.scoring_panels.values():
            for panel in alliance_panels:
                alliance_panels[panel] = False

    def get_num_panels(self, alliance: str):
        return len(self.scoring_panels[alliance])

    def get_num_score_commited(self, alliance: str):
        return sum(self.scoring_panels[alliance].values())

    def register_panel(self, alliance: str, panel: WebSocket):
        self.scoring_panels[alliance][panel] = False

    def set_score_commited(self, alliance: str, panel: WebSocket):
        self.scoring_panels[alliance][panel] = True

    def unregister_panel(self, alliance: str, panel: WebSocket):
        del self.scoring_panels[alliance][panel]
