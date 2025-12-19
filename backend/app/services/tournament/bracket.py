from typing import List
from backend.app.models.match import Match, MatchType, MatchStatus
from backend.app.models.alliance import Alliance


class BracketGenerator:
    @staticmethod
    def generate_double_elimination_8(alliances: List[Alliance]) -> List[Match]:
        """
        Generates the standard FRC Double Elimination Bracket for 8 Alliances.
        Reference: https://www.firstinspires.org/sites/default/files/uploads/resource_library/frc/game-and-season-info/competition-manual/2023/2023-FRC-Competition-Manual.pdf (Section 11.7)
        """
        matches = []

        # Helper to create match
        def create_match(order, short, long, r_src, b_src):
            return Match(
                type=MatchType.PLAYOFF,
                type_order=order,
                short_name=short,
                long_name=long,
                status=MatchStatus.PRE_MATCH,
                red_source=r_src,
                blue_source=b_src,
            )

        # Round 1 (Upper Bracket)
        matches.append(create_match(1, "M1", "Match 1", "A_1", "A_8"))
        matches.append(create_match(2, "M2", "Match 2", "A_4", "A_5"))
        matches.append(create_match(3, "M3", "Match 3", "A_2", "A_7"))
        matches.append(create_match(4, "M4", "Match 4", "A_3", "A_6"))

        # Round 2 (Lower Bracket - Losers of R1)
        matches.append(create_match(5, "M5", "Match 5", "L_M1", "L_M2"))
        matches.append(create_match(6, "M6", "Match 6", "L_M3", "L_M4"))

        # Round 2 (Upper Bracket - Winners of R1)
        matches.append(create_match(7, "M7", "Match 7", "W_M1", "W_M2"))
        matches.append(create_match(8, "M8", "Match 8", "W_M3", "W_M4"))

        # Round 3 (Lower Bracket)
        matches.append(create_match(9, "M9", "Match 9", "L_M8", "W_M5"))
        matches.append(create_match(10, "M10", "Match 10", "L_M7", "W_M6"))

        # Round 4 (Upper Bracket - Semi-Finals)
        matches.append(create_match(11, "M11", "Match 11", "W_M7", "W_M8"))

        # Round 4 (Lower Bracket)
        matches.append(create_match(12, "M12", "Match 12", "W_M10", "W_M9"))

        # Round 5 (Lower Bracket Final)
        matches.append(create_match(13, "M13", "Match 13", "L_M11", "W_M12"))

        # Finals (Best of 3? Or just Finals)
        # FRC Double Elimination ends with Finals (Best of 3) between Winner of M11 and Winner of M13
        matches.append(create_match(14, "F1", "Final 1", "W_M11", "W_M13"))
        matches.append(create_match(15, "F2", "Final 2", "W_M11", "W_M13"))
        matches.append(create_match(16, "F3", "Final 3", "W_M11", "W_M13"))  # If needed

        # Populate initial alliances for Round 1
        # Map alliance name/id to object
        # Assuming alliances are sorted 1-8
        # alliances[0] is Alliance 1

        # We need to populate red1/red2/red3 etc for the first 4 matches
        # But wait, the alliances might not be fully populated yet if we just initialized.
        # Assuming alliances are ready.

        # Actually, we should just set the source. The system should resolve the source to teams later.
        # But for Round 1, we know the teams immediately.

        # Let's resolve Round 1 immediately
        alliance_map = {f"A_{i + 1}": alliances[i] for i in range(len(alliances))}

        for m in matches:
            if m.red_source.startswith("A_"):
                a = alliance_map.get(m.red_source)
                if a:
                    m.playoff_red_alliance = a.id
                    m.red1 = a.captain_team_id or 0
                    m.red2 = a.pick1_team_id or 0
                    m.red3 = a.pick2_team_id or 0

            if m.blue_source.startswith("A_"):
                a = alliance_map.get(m.blue_source)
                if a:
                    m.playoff_blue_alliance = a.id
                    m.blue1 = a.captain_team_id or 0
                    m.blue2 = a.pick1_team_id or 0
                    m.blue3 = a.pick2_team_id or 0

        return matches

    @staticmethod
    def generate_single_elimination_8(alliances: List[Alliance]) -> List[Match]:
        matches = []

        def create_match(order, short, long, r_src, b_src):
            return Match(
                type=MatchType.PLAYOFF,
                type_order=order,
                short_name=short,
                long_name=long,
                status=MatchStatus.PRE_MATCH,
                red_source=r_src,
                blue_source=b_src,
            )

        # Quarter Finals
        matches.append(create_match(1, "QF1-1", "Quarterfinal 1-1", "A_1", "A_8"))
        matches.append(create_match(2, "QF2-1", "Quarterfinal 2-1", "A_4", "A_5"))
        matches.append(create_match(3, "QF3-1", "Quarterfinal 3-1", "A_2", "A_7"))
        matches.append(create_match(4, "QF4-1", "Quarterfinal 4-1", "A_3", "A_6"))

        # Semi Finals
        matches.append(create_match(5, "SF1-1", "Semifinal 1-1", "W_QF1", "W_QF2"))
        matches.append(create_match(6, "SF2-1", "Semifinal 2-1", "W_QF3", "W_QF4"))

        # Finals
        matches.append(create_match(7, "F1", "Final 1", "W_SF1", "W_SF2"))

        # Resolve Round 1
        alliance_map = {f"A_{i + 1}": alliances[i] for i in range(len(alliances))}
        for m in matches:
            if m.red_source.startswith("A_"):
                a = alliance_map.get(m.red_source)
                if a:
                    m.playoff_red_alliance = a.id
                    m.red1 = a.captain_team_id or 0
                    m.red2 = a.pick1_team_id or 0
                    m.red3 = a.pick2_team_id or 0
            if m.blue_source.startswith("A_"):
                a = alliance_map.get(m.blue_source)
                if a:
                    m.playoff_blue_alliance = a.id
                    m.blue1 = a.captain_team_id or 0
                    m.blue2 = a.pick1_team_id or 0
                    m.blue3 = a.pick2_team_id or 0

        return matches
