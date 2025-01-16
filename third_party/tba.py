import base64
import hashlib
from datetime import UTC
from typing import Any

import aiohttp
import orjson
from pydantic import BaseModel

import models
from game.ranking import RankingField
from game.score import ENDGAME_STATUS, Score, ScoreSummary
from models.event import PLAYOFF_TYPE, Event
from models.match import MATCH_TYPE, MatchOut
from models.match_result import MatchResult

TBA_BASE_URL = 'https://www.thebluealliance.com'
TBA_AUTH_KEY = ''
AVATARS_DIR = 'static/img/avatars'


class TbaClient(BaseModel):
    base_url: str
    event_code: str
    secret_id: str
    secret: str
    event_names_cache: dict[str, str]

    @staticmethod
    def get_tba_team(team: int):
        return f'frc{team}'

    @staticmethod
    def create_tba_scoring_breakdown(
        event_settings: Event, match: MatchOut, match_result: MatchResult, alliance: str
    ):
        breakdown = TbaScoreBreakdown()
        score = Score()
        score_summary = ScoreSummary()
        opponent_summary = ScoreSummary()

        if alliance == 'red':
            score = match_result.red_score
            score_summary = match_result.red_score_summary()
            opponent_summary = match_result.blue_score_summary()
        else:
            score = match_result.blue_score
            score_summary = match_result.blue_score_summary()
            opponent_summary = match_result.red_score_summary()

        breakdown.auto_line_robot_1 = leave_mapping[score.leave_statuses[0]]
        breakdown.auto_line_robot_2 = leave_mapping[score.leave_statuses[1]]
        breakdown.auto_line_robot_3 = leave_mapping[score.leave_statuses[2]]
        breakdown.auto_leave_points = score_summary.leave_points
        breakdown.auto_amp_note_count = score.amp_speaker.auto_amp_notes
        breakdown.auto_amp_note_points = 2 * breakdown.auto_amp_note_count
        breakdown.auto_speaker_note_count = score.amp_speaker.auto_speaker_notes
        breakdown.auto_speaker_note_points = 5 * breakdown.auto_speaker_note_count
        breakdown.auto_total_note_points = (
            breakdown.auto_amp_note_points + breakdown.auto_speaker_note_points
        )
        breakdown.auto_points = score_summary.auto_points
        breakdown.teleop_amp_note_count = score.amp_speaker.teleop_amp_notes
        breakdown.teleop_amp_note_points = 1 * breakdown.teleop_amp_note_count
        breakdown.teleop_speaker_note_count = score.amp_speaker.teleop_unamplified_speaker_notes
        breakdown.teleop_speaker_note_points = 2 * breakdown.teleop_speaker_note_count
        breakdown.teleop_speaker_note_amplified_count = (
            score.amp_speaker.teleop_amplified_speaker_notes
        )
        breakdown.teleop_speaker_note_amplified_points = (
            5 * breakdown.teleop_speaker_note_amplified_count
        )
        breakdown.teleop_total_note_points = (
            breakdown.teleop_amp_note_points
            + breakdown.teleop_speaker_note_points
            + breakdown.teleop_speaker_note_amplified_points
        )
        breakdown.endgame_robot_1 = endgame_status_mapping[score.endgame_statuses[0]]
        breakdown.endgame_robot_2 = endgame_status_mapping[score.endgame_statuses[1]]
        breakdown.endgame_robot_3 = endgame_status_mapping[score.endgame_statuses[2]]
        breakdown.endgame_park_points = score_summary.park_points
        breakdown.endgame_onstage_points = score_summary.onstage_points
        breakdown.endgame_harmony_points = score_summary.harmony_points
        breakdown.mic_stage_left = score.microphone_statuses[0]
        breakdown.mic_center_stage = score.microphone_statuses[1]
        breakdown.mic_stage_right = score.microphone_statuses[2]
        breakdown.endgame_spotlight_bonus_points = score_summary.spotlight_points
        breakdown.trap_stage_left = score.trap_statuses[0]
        breakdown.trap_center_stage = score.trap_statuses[1]
        breakdown.trap_stage_right = score.trap_statuses[2]
        breakdown.endgame_note_in_trap_points = score_summary.trap_points
        breakdown.endgame_total_stage_points = score_summary.stage_points
        breakdown.teleop_points = (
            breakdown.teleop_total_note_points + breakdown.endgame_total_stage_points
        )
        breakdown.coopertition_criteria_met = score_summary.coopertition_criteria_met
        breakdown.melody_bonus_achived = score_summary.melody_bonus_ranking_point
        breakdown.ensemble_bonus_achieved = score_summary.ensemble_bonus_ranking_point

        for foul in score.fouls:
            if foul.is_technical:
                breakdown.tech_foul_count += 1
            else:
                breakdown.foul_count += 1
            if foul.rule() is not None and foul.rule().is_ranking_point:
                breakdown.g424_penalty = True

        breakdown.foul_points = score_summary.foul_points
        breakdown.total_points = score_summary.score

        if match.should_update_ranking():
            ranking = RankingField()
            ranking.add_score_summary(score_summary, opponent_summary, False)
            breakdown.rp = ranking.ranking_points

        breakdown_map = breakdown.model_dump()
        if event_settings.melody_bonus_threshold_with_coop == 0:
            del breakdown_map['coopertitionCriteriaMet']
        return breakdown_map

    @classmethod
    def create_tba_alliance(
        cls, team_ids: list[int], surrogates: list[bool], score: int, cards: dict[str, str] | None
    ):
        alliance = TbaAlliance(teams=[], surrogates=[], dqs=[], score=score)
        for i, team_id in enumerate(team_ids):
            if team_id == 0:
                continue
            team_key = cls.get_tba_team(team_id)
            alliance.teams.append(team_key)

            if surrogates[i]:
                alliance.surrogates.append(team_key)

            if cards is not None:
                card = cards.get(str(team_id), None)
                if card is not None and card == 'red':
                    alliance.dqs.append(team_key)

    async def get_team(self, team_number: int):
        path = f'/api/v3/team/{self.get_tba_team(team_number)}'
        resp = await self.get_request(path)
        team_data = TbaTeam(**resp)

        return team_data

    async def get_robot_name(self, team_number: int, year: int):
        path = f'/api/v3/team/{self.get_tba_team(team_number)}/robots'
        robots = await self.get_request(path)

        for robot_dict in robots:
            robot = TbaRobot(**robot_dict)
            if robot.year == year:
                return robot.robot_name

        return ''

    async def get_team_awards(self, team_number: int):
        path = f'/api/v3/team/{self.get_tba_team(team_number)}/awards'
        awards = self.get_request(path)

        for i, award_dict in enumerate(awards):
            award = TbaAward(**award_dict)
            if self.event_names_cache.get(award.event_key) is None:
                self.event_names_cache[award.event_key] = self.get_event_name(award.event_key)
            awards[i].event_name = self.event_names_cache[award.event_key]

        return awards

    async def download_team_avatar(self, team_number: int, year: int):
        path = f'/api/v3/team/{self.get_tba_team(team_number)}/media/{year}'
        medias = self.get_request(path)
        for media_dict in medias:
            media = TbaMediaItem(**media_dict)
            if media.type == 'avatar':
                base64_string = str(media.details['base64Image'])
                avatar_bytes = base64.b64decode(base64_string)
                avatar_path = f'{AVATARS_DIR}/{team_number}.png'
                with open(avatar_path, 'wb') as f:
                    f.write(avatar_bytes)
                return None
        return f'No avatar found for team {team_number} in {year}.'

    async def publish_teams(self):
        teams = models.read_all_teams()
        team_keys = [self.get_tba_team(team.id) for team in teams]
        json_body = orjson.dumps(team_keys)
        resp = await self.post_request('team_list', 'update', json_body)
        if resp['status'] != 200:
            return f'Got status code {resp["status"]} from TBA: {resp["body"]}'
        return None

    async def publish_matches(self):
        qual_matches = models.read_matches_by_type(MATCH_TYPE.qualification, False)
        playoff_matches = models.read_matches_by_type(MATCH_TYPE.playoff, False)
        event_settings = models.read_event_settings()
        matches = qual_matches + playoff_matches
        tba_matches = []

        for match in matches:
            score_breakdown = {'red': {}, 'blue': {}}
            red_score = 0
            blue_score = 0
            red_cards = {}
            blue_cards = {}
            if match.is_complete():
                match_result = models.read_match_result_for_match(match.id)
                if match_result is not None:
                    score_breakdown['red'] = self.create_tba_scoring_breakdown(
                        event_settings, match, match_result, 'red'
                    )
                    score_breakdown['blue'] = self.create_tba_scoring_breakdown(
                        event_settings, match, match_result, 'blue'
                    )
                    red_score = int(score_breakdown['red']['total_points'])
                    blue_score = int(score_breakdown['blue']['total_points'])
                    red_cards = match_result.red_cards
                    blue_cards = match_result.blue_cards
            alliances = {}
            alliances['red'] = self.create_tba_alliance(
                [match.red1, match.red2, match.red3],
                [match.red1_is_surrogate, match.red2_is_surrogate, match.red3_is_surrogate],
                red_score,
                red_cards,
            )
            alliances['blue'] = self.create_tba_alliance(
                [match.blue1, match.blue2, match.blue3],
                [match.blue1_is_surrogate, match.blue2_is_surrogate, match.blue3_is_surrogate],
                blue_score,
                blue_cards,
            )

            tba_matches.append(
                TbaMatch(
                    comp_level=match.tba_match_key.comp_level,
                    set_number=match.tba_match_key.set_number,
                    match_number=match.tba_match_key.match_number,
                    alliances=alliances,
                    score_breakdown=score_breakdown,
                    time_string=match.scheduled_time.strftime('%I:%M %p'),
                    time_utc=match.scheduled_time.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%S'),
                ).model_dump()
            )

        json_body = orjson.dumps(tba_matches)
        resp = await self.post_request('matches', 'update', json_body)
        if resp['status'] != 200:
            return f"Got status code {resp['status']} from TBA: {resp['body']}"
        return None

    async def publish_rankings(self):
        rankings = models.read_all_rankings()

        breakdowns = ['RP', 'Coop', 'Match', 'Auto', 'Stage']
        tba_rankings = [None] * len(rankings)
        for i, rank in enumerate(rankings):
            tba_rankings[i] = TbaRanking(
                team_key=self.get_tba_team(rank.team_id),
                rank=rank.rank,
                rp=float(rank.fields.ranking_points) / float(rank.fields.played),
                coop=float(rank.fields.coopertition_points) / float(rank.fields.played),
                match=float(rank.fields.match_points) / float(rank.fields.played),
                auto=float(rank.fields.auto_points) / float(rank.fields.played),
                stage=float(rank.fields.stage_points) / float(rank.fields.played),
                wins=rank.fields.wins,
                losses=rank.fields.losses,
                ties=rank.fields.ties,
                dqs=rank.fields.disqualifications,
                played=rank.fields.played,
            )

        ranking_list = TbaRankings(breakdowns=breakdowns, rankings=tba_rankings)
        json_body = orjson.dumps(ranking_list.model_dump())

        resp = await self.post_request('rankings', 'update', json_body)
        if resp['status'] != 200:
            return f"Got status code {resp['status']} from TBA: {resp['body']}"
        return None

    async def publish_alliances(self):
        alliances = models.read_all_alliances()

        tba_alliances = []
        for alliance in alliances:
            tba_alliances.append(
                [self.get_tba_team(alliance_team_id) for alliance_team_id in alliance.team_ids]
            )

        json_body = orjson.dumps(tba_alliances)
        resp = await self.post_request('alliance_selections', 'update', json_body)
        if resp['status'] != 200:
            return f"Got status code {resp['status']} from TBA: {resp['body']}"

        event_settings = models.read_event_settings()
        playoff_type = 10 if event_settings.playoff_type == PLAYOFF_TYPE.double_elimination else 0

        resp = await self.post_request('info', 'update', bytes({'playoff_type': playoff_type}))
        if resp['status'] != 200:
            return f"Got status code {resp['status']} from TBA: {resp['body']}"

        return None

    async def publish_awards(self):
        awards = models.read_all_awards()

        tba_awards = []
        for award in awards:
            tba_awards.append(
                TbaPublishedAward(
                    name_str=award.award_name,
                    team_key=self.get_tba_team(award.team_id),
                    awardee=award.person_name,
                ).model_dump()
            )
        json_body = orjson.dumps(tba_awards)
        resp = await self.post_request('awards', 'update', json_body)
        if resp['status'] != 200:
            return f"Got status code {resp['status']} from TBA: {resp['body']}"

        return None

    async def delete_published_matches(self):
        resp = await self.post_request('matches', 'delete_all', bytes(self.event_code))
        if resp['status'] != 200:
            return f"Got status code {resp['status']} from TBA: {resp['body']}"

        return None

    async def get_event_name(self, event_code: str):
        path = f'/api/v3/event/{event_code}'
        event_dict = await self.get_request(path)
        event = TbaEvent(**event_dict)
        return event.name

    async def get_request(self, path: str):
        url = self.base_url + path
        header = {'X-TBA-Auth-Key': TBA_AUTH_KEY}

        async with aiohttp.request('GET', url, headers=header) as resp:
            return await resp.json()

    async def post_request(self, resource: str, action: str, body: bytes):
        path = f'/api/trusted/v1/event/{self.event_code}/{resource}/{action}'
        hash_data = bytes((self.secret + path).encode('ascii'))
        hash_data += body
        signature = f'{hashlib.md5(hash_data).hexdigest()}'
        headers = {'X-TBA-Auth-Id': self.secret_id, 'X-TBA-Auth-Sig': signature}

        async with aiohttp.request(
            'POST', self.base_url + path, body=body, headers=headers
        ) as resp:
            response = {}
            response['status'] = resp.status
            response['body'] = await resp.json()
            return response


class TbaMatch(BaseModel):
    comp_level: str
    set_number: int
    match_number: int
    alliances: dict[str, 'TbaAlliance']
    score_breakdown: dict[str, dict[str, Any]]
    time_string: str
    time_utc: str
    display_name: str


class TbaAlliance(BaseModel):
    teams: list[str]
    surrogates: list[str]
    dqs: list[str]
    score: int


class TbaScoreBreakdown(BaseModel):
    auto_line_robot_1: str = ''
    auto_line_robot_2: str = ''
    auto_line_robot_3: str = ''
    auto_leave_points: int = 0
    auto_amp_note_count: int = 0
    auto_amp_note_points: int = 0
    auto_speaker_note_count: int = 0
    auto_speaker_note_points: int = 0
    auto_total_note_points: int = 0
    auto_points: int = 0
    teleop_amp_note_count: int = 0
    teleop_amp_note_points: int = 0
    teleop_speaker_note_count: int = 0
    teleop_speaker_note_points: int = 0
    teleop_speaker_note_amplified_count: int = 0
    teleop_speaker_note_amplified_points: int = 0
    teleop_total_note_points: int = 0
    endgame_robot_1: str = ''
    endgame_robot_2: str = ''
    endgame_robot_3: str = ''
    endgame_park_points: int = 0
    endgame_onstage_points: int = 0
    endgame_harmony_points: int = 0
    mic_stage_left: bool = False
    mic_center_stage: bool = False
    mic_stage_right: bool = False
    endgame_spotlight_bonus_points: int = 0
    trap_stage_left: bool = False
    trap_center_stage: bool = False
    trap_stage_right: bool = False
    endgame_note_in_trap_points: int = 0
    endgame_total_stage_points: int = 0
    teleop_points: int = 0
    coopertition_criteria_met: bool = False
    melody_bonus_achived: bool = False
    ensemble_bonus_achieved: bool = False
    foul_count: int = 0
    tech_foul_count: int = 0
    g424_penalty: bool = False
    foul_points: int = 0
    total_points: int = 0
    rp: int = 0

    class Config:
        alias = {
            'auto_line_robot_1': 'autoLineRobot1',
            'auto_line_robot_2': 'autoLineRobot2',
            'auto_line_robot_3': 'autoLineRobot3',
            'auto_leave_points': 'autoLeavePoints',
            'auto_amp_note_count': 'autoAmpNoteCount',
            'auto_amp_note_points': 'autoAmpNotePoints',
            'auto_speaker_note_count': 'autoSpeakerNoteCount',
            'auto_speaker_note_points': 'autoSpeakerNotePoints',
            'auto_total_note_points': 'autoTotalNotePoints',
            'auto_points': 'autoPoints',
            'teleop_amp_note_count': 'teleopAmpNoteCount',
            'teleop_amp_note_points': 'teleopAmpNotePoints',
            'teleop_speaker_note_count': 'teleopSpeakerNoteCount',
            'teleop_speaker_note_points': 'teleopSpeakerNotePoints',
            'teleop_speaker_note_amplified_count': 'teleopSpeakerNoteAmplifiedCount',
            'teleop_speaker_note_amplified_points': 'teleopSpeakerNoteAmplifiedPoints',
            'teleop_total_note_points': 'teleopTotalNotePoints',
            'endgame_robot_1': 'endGameRobot1',
            'endgame_robot_2': 'endGameRobot2',
            'endgame_robot_3': 'endGameRobot3',
            'endgame_park_points': 'endGameParkPoints',
            'endgame_onstage_points': 'endGameOnStagePoints',
            'endgame_harmony_points': 'endGameHarmonyPoints',
            'mic_stage_left': 'micStageLeft',
            'mic_center_stage': 'micCenterStage',
            'mic_stage_right': 'micStageRight',
            'endgame_spotlight_bonus_points': 'endGameSpotLightBonusPoints',
            'trap_stage_left': 'trapStageLeft',
            'trap_center_stage': 'trapCenterStage',
            'trap_stage_right': 'trapStageRight',
            'endgame_note_in_trap_points': 'endGameNoteInTrapPoints',
            'endgame_total_stage_points': 'endGameTotalStagePoints',
            'teleop_points': 'teleopPoints',
            'coopertition_criteria_met': 'coopertitionCriteriaMet',
            'melody_bonus_achived': 'melodyBonusAchieved',
            'ensemble_bonus_achieved': 'ensembleBonusAchieved',
            'foul_count': 'foulCount',
            'tech_foul_count': 'techFoulCount',
            'g424_penalty': 'g424Penalty',
            'foul_points': 'foulPoints',
            'total_points': 'totalPoints',
            'rp': 'rp',
        }
        populate_by_name = True


class TbaRanking(BaseModel):
    team_key: str
    rank: int
    rp: float
    coop: float
    match: float
    auto: float
    stage: float
    wins: int
    losses: int
    ties: int
    dqs: int
    played: int


class TbaRankings(BaseModel):
    breakdowns: list[str]
    rankings: list[TbaRanking]


class TbaTeam(BaseModel):
    team_number: int
    name: str
    nickname: str
    city: str
    state_prov: str
    country: str
    rookie_year: int


class TbaRobot(BaseModel):
    robot_name: str
    year: int


class TbaAward(BaseModel):
    name: str
    event_key: str
    year: int
    event_name: str


class TbaEvent(BaseModel):
    name: str


class TbaMediaItem(BaseModel):
    details: dict[str, Any]
    type: str


class TbaPublishedAward(BaseModel):
    name_str: str
    team_key: str
    awardee: str


leave_mapping = {False: 'No', True: 'Yes'}
endgame_status_mapping = {
    ENDGAME_STATUS.none: 'None',
    ENDGAME_STATUS.park: 'Parked',
    ENDGAME_STATUS.stage_left: 'StageLeft',
    ENDGAME_STATUS.stage_center: 'CenterStage',
    ENDGAME_STATUS.stage_right: 'StageRight',
}


def new_tba_client(event_code: str, secret_id: str, secret: str):
    return TbaClient(
        base_url=TBA_BASE_URL,
        event_code=event_code,
        secret_id=secret_id,
        secret=secret,
        event_names_cache={},
    )
