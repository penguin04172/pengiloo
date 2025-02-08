import asyncio
from datetime import datetime, timedelta
from io import BytesIO, StringIO

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from fpdf import FPDF
from pydantic import BaseModel

import game
import models
import tournament

from .api.bracket_svg import generate_bracket_svg
from .arena import get_arena
from .template_config import templates


class PDF(FPDF):
    def footer(self):
        self.set_y(-10)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 0, 'C')


router = APIRouter(prefix='/reports', tags=['reports'])


@router.get('/csv/rankings')
async def get_csv_rankings(request: Request):
    return templates.TemplateResponse(
        request,
        'reports/rankings.csv.jinja',
        {'rankings': models.read_all_rankings()},
        media_type='text/plain',
        headers={'Content-Disposition': 'inline; filename="rankings.csv"'},
    )


@router.get('/pdf/rankings')
async def get_pdf_rankings(request: Request) -> StreamingResponse:
    rankings = models.read_all_rankings()

    pdf = PDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()

    # 標題
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(195, 10, f'Team Standings - {get_arena().event.name}', ln=True, align='C')
    pdf.ln(5)

    # 表格標題
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font('Arial', 'B', 10)

    col_widths = {
        'Rank': 13,
        'Team': 20,
        'RP': 20,
        'Coop': 20,
        'Match': 20,
        'Auto': 20,
        'Stage': 20,
        'W-L-T': 22,
        'DQ': 20,
        'Played': 20,
    }
    row_height = 6.5
    headers = ['Rank', 'Team', 'RP', 'Coop', 'Match', 'Auto', 'Barge', 'W-L-T', 'DQ', 'Played']

    for col in headers:
        pdf.cell(col_widths[col], row_height, col, border=1, align='C', fill=True)

    pdf.ln(row_height)

    # 填充排名數據
    for ranking in rankings:
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(col_widths['Rank'], row_height, str(ranking.rank), border=1, align='C')

        pdf.set_font('Arial', '', 10)
        pdf.cell(col_widths['Team'], row_height, str(ranking.team_id), border=1, align='C')
        pdf.cell(col_widths['RP'], row_height, str(ranking.ranking_points), border=1, align='C')
        pdf.cell(
            col_widths['Coop'], row_height, str(ranking.coopertition_points), border=1, align='C'
        )
        pdf.cell(col_widths['Match'], row_height, str(ranking.match_points), border=1, align='C')
        pdf.cell(col_widths['Auto'], row_height, str(ranking.auto_points), border=1, align='C')
        pdf.cell(col_widths['Barge'], row_height, str(ranking.barge_points), border=1, align='C')

        record = f'{ranking.wins}-{ranking.losses}-{ranking.ties}'
        pdf.cell(col_widths['W-L-T'], row_height, record, border=1, align='C')

        pdf.cell(col_widths['DQ'], row_height, str(ranking.disqualifications), border=1, align='C')
        pdf.cell(col_widths['Played'], row_height, str(ranking.played), border=1, align='C')

        pdf.ln(row_height)

    # **將 PDF 存入記憶體（BytesIO）**
    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))
    pdf_bytes.seek(0)  # **將指標移到開始，準備傳輸**

    return StreamingResponse(
        pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="rankings.pdf"'},
    )


def find_backup_teams(rankings: game.Rankings) -> tuple[game.Rankings, dict[int, bool]]:
    pruned = game.Rankings()

    alliances = models.read_all_alliances()

    if len(alliances) == 0:
        raise ValueError('No alliances found in the database')

    picked_teams = {}
    picked_backups = {}

    for alliance in alliances:
        picked_teams.fromkeys(alliance.team_ids[0:3], True)
        if len(alliance.team_ids) > 3:
            picked_backups.fromkeys(alliance.team_ids[3:4], True)

    for rank in rankings:
        if rank.team_id not in picked_teams:
            pruned.append(rank)

    return pruned, picked_backups


class BackupTeam(BaseModel):
    rank: int
    called: bool
    team_id: int
    ranking_points: int


@router.get('/csv/backup_teams')
async def get_csv_backup_teams(request: Request):
    rankings = models.read_all_rankings()

    rankings, picked_backups = await asyncio.to_thread(find_backup_teams, rankings)

    backup_teams = [
        BackupTeam(
            rank=rank.rank,
            called=picked_backups[rank.team_id],
            team_id=rank.team_id,
            ranking_points=rank.ranking_points,
        )
        for rank in rankings
    ]

    return templates.TemplateResponse(
        request,
        'reports/backups.csv.jinja',
        {'backup_teams': backup_teams},
        media_type='text/plain',
        headers={'Content-Disposition': 'inline; filename="backups.csv"'},
    )


@router.get('/pdf/backup_teams')
async def get_pdf_backup_teams(request: Request) -> StreamingResponse:
    rankings = models.read_all_rankings()

    rankings, picked_backups = await asyncio.to_thread(find_backup_teams, rankings)

    col_widths = {'Rank': 20, 'Called': 25, 'Team': 25, 'RP': 25}
    row_height = 8

    pdf = PDF('P', 'mm', 'Letter')
    pdf.add_page()
    pdf.set_fill_color(220, 220, 220)

    # Render table header
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(col_widths['Rank'], row_height, 'Rank', border=1, align='C', fill=True)
    pdf.cell(col_widths['Called'], row_height, 'Called?', border=1, align='C', fill=True)
    pdf.cell(col_widths['Team'], row_height, 'Team', border=1, align='C', fill=True)
    pdf.cell(col_widths['RP'], row_height, 'RP', border=1, align='C', fill=True)
    pdf.ln(row_height)

    # Render table rows
    for ranking in rankings:
        picked = 'Y' if picked_backups[ranking.team_id] else ''
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(col_widths['Rank'], row_height, str(ranking.rank), border=1, align='C')
        pdf.cell(col_widths['Called'], row_height, picked, border=1, align='C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(col_widths['Team'], row_height, str(ranking.team_id), border=1, align='C')
        pdf.cell(col_widths['RP'], row_height, str(ranking.ranking_points), border=1, align='C')
        pdf.ln(row_height)

    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))
    pdf_bytes.seek(0)

    return StreamingResponse(
        pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="backups.pdf"'},
    )


# 所有單位為 mm
C_H_PAD = 5
C_V_PAD = 5
C_WIDTH = 95
C_HEIGHT = 60
C_SIDE_MARGIN = 10
C_TOP_MARGIN = 10
C_IMG_WIDTH = 50
C_W_OFFSET = 5


def _draw_pdf_logo(pdf: FPDF, x: float, y: float, width: float):
    pdf.image('static/img/logo.png', x - (width / 2), y - 25, width, 0, 'PNG')


def _draw_centered_text(pdf: FPDF, text: str, x: float, y: float):
    width = pdf.get_string_width(text)
    pdf.text(x - (width / 2), y, text)


def _draw_event_watermark(pdf: FPDF, x: float, y: float, event_name: str):
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(192, 192, 192)
    text_width = pdf.get_string_width(event_name)

    pdf.rotate(90, x, y)
    pdf.text(x - (text_width / 2), y - C_WIDTH / 2 + C_W_OFFSET, event_name)
    pdf.rotate(0)

    pdf.rotate(270, x, y)
    pdf.text(x - (text_width / 2), y + C_WIDTH / 2 - C_W_OFFSET, event_name)
    pdf.rotate(0)


def _draw_backup_coupon(
    pdf: FPDF, event_name: str, x: float, y: float, team_id: int, alliance_number: int
):
    pdf.set_text_color(0, 0, 0)
    _draw_pdf_logo(pdf, x, y, C_IMG_WIDTH)

    pdf.set_font('Arial', 'B', 24)
    _draw_centered_text(pdf, 'Backup Coupon', x, y + 10)

    pdf.set_font('Arial', 'B', 14)
    _draw_centered_text(pdf, f'Alliance: {alliance_number}    Captain: {team_id}', x, y + 20)
    _draw_event_watermark(pdf, x, y, event_name)


def _draw_timeout_coupon(
    pdf: FPDF, event_name: str, x: float, y: float, team_id: int, alliance_number: int
):
    pdf.set_text_color(0, 0, 0)
    _draw_pdf_logo(pdf, x, y, C_IMG_WIDTH)

    pdf.set_font('Arial', 'B', 24)
    _draw_centered_text(pdf, 'Timeout Coupon', x, y + 10)

    pdf.set_font('Arial', 'B', 14)
    _draw_centered_text(pdf, f'Alliance: {alliance_number}    Captain: {team_id}', x, y + 20)
    _draw_event_watermark(pdf, x, y, event_name)


@router.get('/pdf/coupons')
async def get_pdf_coupons(request: Request) -> StreamingResponse:
    pdf = FPDF('P', 'mm', 'Letter')
    pdf.set_line_width(1)

    alliances = models.read_all_alliances()
    if len(alliances) == 0:
        raise HTTPException(400, 'No alliances found in the database')

    event_name = get_arena().event.name
    for page in range(0, int((len(alliances) + 3) / 4)):
        height_acc = C_TOP_MARGIN
        pdf.add_page()
        for i in range(page * 4, page * 4 + 4):
            if i >= len(alliances):
                break
            alliance_captain = alliances[i].team_ids[0]
            pdf.set_fill_color(220, 220, 220)

            pdf.rect(C_SIDE_MARGIN, float(height_acc), C_WIDTH, C_HEIGHT, 'D', True, 4)
            timeout_x = C_SIDE_MARGIN + C_WIDTH * 0.5
            timeout_y = float(height_acc) + C_HEIGHT * 0.5
            _draw_timeout_coupon(pdf, event_name, timeout_x, timeout_y, alliance_captain, i + 1)

            pdf.rect(
                C_SIDE_MARGIN + C_WIDTH + C_H_PAD,
                float(height_acc),
                C_WIDTH,
                C_HEIGHT,
                'D',
                True,
                4,
            )
            backup_x = C_SIDE_MARGIN + C_WIDTH + C_H_PAD + C_WIDTH * 0.5
            backup_y = float(height_acc) + C_HEIGHT * 0.5
            height_acc += C_HEIGHT + C_V_PAD
            _draw_backup_coupon(pdf, event_name, backup_x, backup_y, alliance_captain, i + 1)

    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))
    pdf_bytes.seek(0)

    return StreamingResponse(
        pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="coupons.pdf"'},
    )


@router.get('/csv/schedule/{type}')
async def get_csv_schedule(request: Request, type: str):
    try:
        match_type = models.MatchType[type.upper()]
    except KeyError as e:
        raise HTTPException(400, f'Invalid match type: {type}') from e

    matches = models.read_matches_by_type(match_type, False)

    return templates.TemplateResponse(
        request,
        'reports/schedule.csv.jinja',
        {'matches': matches},
        media_type='text/plain',
        headers={'Content-Disposition': 'inline; filename="schedule.csv"'},
    )


@router.get('/pdf/schedule/{type}')
async def get_pdf_schedule(requset: Request, type: str) -> StreamingResponse:
    try:
        match_type = models.MatchType[type.upper()]
    except KeyError as e:
        raise HTTPException(400, f'Invalid match type: {type}') from e

    matches = models.read_matches_by_type(match_type, False)

    scheduled_breaks = models.read_scheduled_breaks_by_match_type(match_type)

    break_index = 0
    teams = models.read_all_teams()

    matches_per_team = 0
    if len(teams) > 0:
        matches_per_team = len(matches) * tournament.TEAMS_PER_MATCH // len(teams)

    col_widths = {'Time': 35, 'Match': 40, 'Team': 20}
    row_height = 6.5

    pdf = PDF('P', 'mm', 'Letter')
    pdf.add_page()

    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(195, 10, f'Match Schedule - {get_arena().event.name}', ln=True, align='C')

    pdf.cell(col_widths['Time'], row_height, 'Time', border=1, align='C', fill=True)
    pdf.cell(col_widths['Match'], row_height, 'Match', border=1, align='C', fill=True)
    pdf.cell(col_widths['Team'], row_height, 'Red 1', border=1, align='C', fill=True)
    pdf.cell(col_widths['Team'], row_height, 'Red 2', border=1, align='C', fill=True)
    pdf.cell(col_widths['Team'], row_height, 'Red 3', border=1, align='C', fill=True)
    pdf.cell(col_widths['Team'], row_height, 'Blue 1', border=1, align='C', fill=True)
    pdf.cell(col_widths['Team'], row_height, 'Blue 2', border=1, align='C', fill=True)
    pdf.cell(col_widths['Team'], row_height, 'Blue 3', border=1, align='C', fill=True)
    pdf.ln(row_height)

    def format_team(team_id):
        return '' if team_id == 0 else str(team_id)

    def surrogate_text(surrogate):
        return '(surrogate)' if surrogate else ''

    pdf.set_font('Arial', '', 10)
    for match in matches:
        if (
            break_index < len(scheduled_breaks)
            and scheduled_breaks[break_index].type_order_before == match.type_order
        ):
            scheduled_break = scheduled_breaks[break_index]
            formatted_time = scheduled_break.time.strftime('%B %m/%d %I:%M %p')
            description = (
                f'{scheduled_break.description} ({scheduled_break.duration_sec//60} minutes)'
            )
            pdf.cell(col_widths['Time'], row_height, formatted_time, border=1, align='C')
            pdf.cell(
                col_widths['Match'] + 6 * col_widths['Team'],
                row_height,
                description,
                border=1,
                align='C',
            )
            pdf.ln(row_height)
            break_index += 1

        height = row_height
        border_str = 1
        align_str = 'C'
        surrogate = any(
            [
                match.blue1_is_surrogate,
                match.blue2_is_surrogate,
                match.blue3_is_surrogate,
                match.red1_is_surrogate,
                match.red2_is_surrogate,
                match.red3_is_surrogate,
            ]
        )

        if surrogate:
            height = 5.0
            border_str = 'LTR'
            align_str = 'CB'

        pdf.cell(
            col_widths['Time'],
            height,
            datetime.strptime(match.scheduled_time, '%Y-%m-%d %H:%M:%S').strftime('%b %d %I:%M %p'),
            border=border_str,
            align=align_str,
        )
        pdf.cell(col_widths['Match'], height, match.long_name, border=border_str, align=align_str)
        pdf.cell(
            col_widths['Team'], height, format_team(match.red1), border=border_str, align=align_str
        )
        pdf.cell(
            col_widths['Team'], height, format_team(match.red2), border=border_str, align=align_str
        )
        pdf.cell(
            col_widths['Team'], height, format_team(match.red3), border=border_str, align=align_str
        )
        pdf.cell(
            col_widths['Team'], height, format_team(match.blue1), border=border_str, align=align_str
        )
        pdf.cell(
            col_widths['Team'], height, format_team(match.blue2), border=border_str, align=align_str
        )
        pdf.cell(
            col_widths['Team'], height, format_team(match.blue3), border=border_str, align=align_str
        )
        pdf.ln(height)

        if surrogate:
            height = 4.0
            pdf.set_font('Arial', '', 8)
            pdf.cell(col_widths['Time'], height, '', border='LBR', align='C')
            pdf.cell(col_widths['Match'], height, '', border='LBR', align='C')
            pdf.cell(
                col_widths['Team'],
                height,
                surrogate_text(match.red1_is_surrogate),
                border='LBR',
                align='C',
            )
            pdf.cell(
                col_widths['Team'],
                height,
                surrogate_text(match.red2_is_surrogate),
                border='LBR',
                align='C',
            )
            pdf.cell(
                col_widths['Team'],
                height,
                surrogate_text(match.red3_is_surrogate),
                border='LBR',
                align='C',
            )
            pdf.cell(
                col_widths['Team'],
                height,
                surrogate_text(match.blue1_is_surrogate),
                border='LBR',
                align='C',
            )
            pdf.cell(
                col_widths['Team'],
                height,
                surrogate_text(match.blue2_is_surrogate),
                border='LBR',
                align='C',
            )
            pdf.cell(
                col_widths['Team'],
                height,
                surrogate_text(match.blue3_is_surrogate),
                border='LBR',
                align='C',
            )
            pdf.ln(height)
            pdf.set_font('Arial', '', 10)

    if match_type != models.MatchType.PLAYOFF:
        pdf.cell(195, 10, f'Matches per team: {matches_per_team}', ln=True, align='L')

    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))
    pdf_bytes.seek(0)

    return StreamingResponse(
        pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="schedule.pdf"'},
    )


@router.get('/csv/teams')
async def get_csv_teams(request: Request):
    return templates.TemplateResponse(
        request,
        'reports/teams.csv.jinja',
        {'teams': models.read_all_teams()},
        media_type='text/plain',
        headers={'Content-Disposition': 'inline; filename="teams.csv"'},
    )


@router.get('/pdf/teams')
async def get_pdf_teams(request: Request, show_has_connected: bool) -> StreamingResponse:
    teams = models.read_all_teams()

    col_widths = {'Id': 12, 'Name': 80, 'Location': 80, 'RookieYear': 23}
    if show_has_connected:
        col_widths['HasConnected'] = 25
    row_height = 6.5
    line_height = 5.0

    pdf = PDF('P', 'mm', 'Letter')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(220, 220, 220)

    pdf.cell(195, 10, f'Team List - {get_arena().event.name}', ln=True, align='C')
    pdf.cell(col_widths['Id'], row_height, 'Id', border=1, align='C', fill=True)
    pdf.cell(col_widths['Name'], row_height, 'Name', border=1, align='C', fill=True)
    pdf.cell(col_widths['Location'], row_height, 'Location', border=1, align='C', fill=True)
    pdf.cell(col_widths['RookieYear'], row_height, 'Rookie Year', border=1, align='C', fill=True)
    if show_has_connected:
        pdf.cell(
            col_widths['HasConnected'], row_height, 'Has Connected', border=1, align='C', fill=True
        )
    pdf.ln(row_height)

    pdf.set_font('Arial', '', 10)
    for team in teams:
        num_nickname_rows = len(
            pdf.multi_cell(
                col_widths['Name'], line_height, team.nickname, align='L', split_only=True
            )
        )
        location = f'{team.city}, {team.state_prov}, {team.country}'
        num_location_rows = len(
            pdf.multi_cell(
                col_widths['Location'], line_height, location, align='L', split_only=True
            )
        )
        team_row_height = max(num_nickname_rows, num_location_rows) * line_height
        pdf.cell(col_widths['Id'], team_row_height, str(team.id), border=1, align='L')
        _draw_multi_line_cell(
            pdf,
            col_widths['Name'],
            team_row_height,
            line_height,
            team.nickname,
            'L',
            num_nickname_rows,
        )
        _draw_multi_line_cell(
            pdf,
            col_widths['Location'],
            team_row_height,
            line_height,
            location,
            'L',
            num_location_rows,
        )
        pdf.cell(
            col_widths['RookieYear'], team_row_height, str(team.rookie_year), border=1, align='L'
        )
        if show_has_connected:
            pdf.cell(
                col_widths['HasConnected'],
                team_row_height,
                'Yes' if team.has_connected else '',
                border=1,
                align='L',
            )
        pdf.ln(team_row_height)

    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))
    pdf_bytes.seek(0)

    return StreamingResponse(
        pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="teams.pdf"'},
    )


@router.get('/csv/wpakeys')
async def get_csv_wpakeys(request: Request):
    return StreamingResponse(
        'Team,WPAPassword\n'
        + '\n'.join(f'{team.id},{team.wpakey}' for team in models.read_all_teams()),
        headers={'Content-Disposition': 'attachment; filename="wpakeys.csv"'},
        media_type='text/csv',
    )


@router.get('/pdf/alliances')
async def get_pdf_alliances(request: Request) -> StreamingResponse:
    alliances = models.read_all_alliances()

    alliance_statuses = {}
    if get_arena().playoff_tournament.is_complete():
        alliance_statuses[get_arena().playoff_tournament.winning_alliance_id()] = 'Winner'
        alliance_statuses[get_arena().playoff_tournament.finalist_alliance_id()] = 'Finalist'

    def update_alliance_status(matchup):
        if matchup.is_complete():
            if (
                matchup.losing_alliance_id() not in alliance_statuses
                and matchup.is_losing_alliance_eliminated()
            ):
                alliance_statuses[matchup.losing_alliance_id()] = f'Eliminated in {matchup.Id()}'
            else:
                if matchup.red_alliance_id > 0:
                    alliance_statuses[matchup.red_alliance_id] = f'Playing in {matchup.Id()}'
                if matchup.blue_alliance_id > 0:
                    alliance_statuses[matchup.blue_alliance_id] = f'Playing in {matchup.Id()}'

    get_arena().playoff_tournament.traverse(update_alliance_status)

    teams = models.read_all_teams()
    teams_dict = {team.id: team for team in teams}

    col_widths = {'Alliance': 23, 'Id': 12, 'Name': 80, 'Location': 80}
    row_height = 6.5
    line_height = 5.0

    pdf = PDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(220, 220, 220)

    event_name = 'Playoff Alliances - ' + get_arena().event.name
    pdf.cell(195, row_height, event_name, ln=1, align='C')

    pdf.cell(col_widths['Alliance'], row_height, 'Alliance', border=1, align='C', fill=True)
    pdf.cell(col_widths['Id'], row_height, 'Team', border=1, align='C', fill=True)
    pdf.cell(col_widths['Name'], row_height, 'Name', border=1, align='C', fill=True)
    pdf.cell(col_widths['Location'], row_height, 'Location', border=1, ln=1, align='C', fill=True)
    pdf.set_font('Arial', '', 10)

    start_x = pdf.get_x()
    for alliance in alliances:
        alliance_height = 0.0
        for team_id in alliance.team_ids:
            team = teams_dict[team_id]
            num_nickname_rows = len(
                pdf.multi_cell(col_widths['Name'], line_height, team.nickname, split_only=True)
            )
            location = f'{team.city}, {team.state_prov}, {team.country}'
            num_location_rows = len(
                pdf.multi_cell(col_widths['Location'], line_height, location, split_only=True)
            )
            num_rows = max(num_nickname_rows, num_location_rows)
            team_row_height = row_height if num_rows == 1 else line_height * num_rows
            alliance_height += team_row_height

        num_alliance_statuses_rows = len(
            pdf.multi_cell(
                col_widths['Alliance'],
                line_height,
                alliance_statuses[alliance.id],
                split_only=True,
            )
        )
        _draw_multi_line_cell(
            col_widths['Alliance'],
            alliance_height,
            line_height,
            f'Alliance {alliance.id}\n{alliance_statuses[alliance.id]}',
            'C',
            num_alliance_statuses_rows + 1,
        )

        for team_id in alliance['TeamIds']:
            team = teams_dict[team_id]
            num_nickname_rows = len(
                pdf.multi_cell(col_widths['Name'], line_height, team.nickname, split_only=True)
            )
            location = f'{team.city}, {team.state_prov}, {team.country}'
            num_location_rows = len(
                pdf.multi_cell(col_widths['Location'], line_height, location, split_only=True)
            )
            num_rows = max(num_nickname_rows, num_location_rows)
            team_row_height = row_height if num_rows == 1 else line_height * num_rows

            pdf.cell(col_widths['Id'], team_row_height, str(team.id), border=1, align='L')
            _draw_multi_line_cell(
                col_widths['Name'],
                team_row_height,
                line_height,
                team.nickname,
                'L',
                num_nickname_rows,
            )
            _draw_multi_line_cell(
                col_widths['Location'],
                team_row_height,
                line_height,
                location,
                'L',
                num_location_rows,
            )

            pdf.set_xy(start_x + col_widths['Alliance'], pdf.get_y() + team_row_height)

        pdf.set_x(start_x)
        pdf.ln(alliance_height)

    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))
    pdf_bytes.seek(0)

    return StreamingResponse(
        pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="alliances.pdf"'},
    )


@router.get('/pdf/bracket')
async def get_pdf_bracket(request: Request) -> StreamingResponse:
    svg = await generate_bracket_svg(None)

    return templates.TemplateResponse(
        request,
        'reports/bracket.html.jinja',
        {'svg': svg},
    )


@router.get('/pdf/cycle/{type}')
async def get_pdf_cycle(request: Request, type: str):
    try:
        cycle_type = models.MatchType[type.upper()]
    except KeyError as e:
        raise HTTPException(400, f'Invalid match type: {type.upper()}') from e

    matches = models.read_matches_by_type(cycle_type, False)

    col_widths = {'Time': 30, 'Time2': 22, 'Match': 15, 'Diff': 20}
    row_height = 6.5

    pdf = PDF('P', 'mm', 'Letter')
    pdf.add_page()

    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(
        195,
        row_height,
        f'{cycle_type.name.capitalize()} Cycle Time - {get_arena().event.name}',
        ln=True,
        align='C',
    )
    pdf.cell(col_widths['Match'], row_height, 'Match', border=1, align='C', fill=True)
    pdf.cell(col_widths['Time'], row_height, 'Scheduled Time', border=1, align='C', fill=True)
    pdf.cell(col_widths['Time2'], row_height, 'Ready', border=1, align='C', fill=True)
    pdf.cell(col_widths['Time2'], row_height, 'Started', border=1, align='C', fill=True)
    pdf.cell(col_widths['Time2'], row_height, 'Commited', border=1, align='C', fill=True)
    pdf.cell(col_widths['Diff'], row_height, 'Cycle Time', border=1, align='C', fill=True)
    pdf.cell(col_widths['Diff'], row_height, 'Delta Time', border=1, align='C', fill=True)
    pdf.cell(col_widths['Diff'], row_height, 'MC Time', border=1, align='C', fill=True)
    pdf.cell(col_widths['Diff'], row_height, 'Ref Time', border=1, align='C', fill=True)

    pdf.set_font('Arial', '', 10)
    last_match = None
    for match in matches:
        height = row_height
        border_str = '1'
        align_str = 'CM'

        field_ready = (
            '' if match.field_ready_at is None else match.field_ready_at.strftime('%I:%M %p')
        )

        started_at = '' if match.started_at is None else match.started_at.strftime('%I:%M %p')

        score_committed = (
            '' if match.score_commit_at is None else match.score_commit_at.strftime('%I:%M %p')
        )

        ref_time = ''
        if match.started_at is not None and match.score_commit_at is not None:
            temp_ref_time = match.score_commit_at - (
                match.started_at + timedelta(seconds=game.timing.get_duration_to_teleop_end())
            )
            ref_time = str(temp_ref_time.seconds // 60) + ':' + str(temp_ref_time.seconds % 60)

        mc_time = ''
        if match.started_at is not None and match.field_ready_at is not None:
            temp_mc_time = match.started_at - match.field_ready_at
            mc_time = str(temp_mc_time.seconds // 60) + ':' + str(temp_mc_time.seconds % 60)

        delta_time = ''
        if match.started_at is not None:
            temp_delta_time = match.started_at - match.scheduled_time
            delta_time = (
                str(temp_delta_time.seconds // 60) + ':' + str(temp_delta_time.seconds % 60)
            )

        cycle_time = ''
        if last_match is not None and match.started_at is not None:
            temp_cycle_time = match.started_at - last_match
            cycle_time = (
                str(temp_cycle_time.seconds // 60) + ':' + str(temp_cycle_time.seconds % 60)
            )

        last_match = match.started_at

        pdf.cell(col_widths['Match'], height, match.short_name, border=border_str, align=align_str)
        pdf.cell(
            col_widths['Time'], height, match.scheduled_time.strftime('%m/%d %I:%M %p'), border=1
        )
        pdf.cell(col_widths['Time2'], height, field_ready, border=1)
        pdf.cell(col_widths['Time2'], height, started_at, border=1)
        pdf.cell(col_widths['Time2'], height, score_committed, border=1)
        pdf.cell(col_widths['Diff'], height, cycle_time, border=1)
        pdf.cell(col_widths['Diff'], height, delta_time, border=1)
        pdf.cell(col_widths['Diff'], height, mc_time, border=1)
        pdf.cell(col_widths['Diff'], height, ref_time, border=1)
        pdf.ln(height)

    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))
    pdf_bytes.seek(0)

    return StreamingResponse(
        pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="cycle.pdf"'},
    )


@router.get('/csv/fta')
async def get_csv_fta(request: Request):
    return templates.TemplateResponse(
        request,
        'reports/fta.csv.jinja',
        {'teams': models.read_all_teams()},
        media_type='text/plain',
        headers={'Content-Disposition': 'inline; filename="fta.csv"'},
    )


def _draw_multi_line_cell(
    pdf: FPDF,
    width: float,
    height: float,
    line_height: float,
    text: str,
    align: str,
    num_text_lines: int,
):
    start_x, start_y = pdf.get_x(), pdf.get_y()
    pdf.rect(start_x, start_y, width, height)

    gap_y = float(height - (line_height * num_text_lines)) / 2
    pdf.set_y(start_y + gap_y)
    pdf.multi_cell(width, line_height, text, align=align)

    pdf.set_xy(start_x + width, start_y)
