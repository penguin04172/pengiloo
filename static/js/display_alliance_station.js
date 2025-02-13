const $ = selector => document.querySelector(selector);
const $$ = selector => document.querySelectorAll(selector);

let station = "";
let blinkInterval;
let currentScreen = "blank";
let websocket;

function handleAllianceStationDisplayMode (targetScreen) {
    currentScreen = targetScreen;
    if (station !== "") {
        let body = $('body');
        body.setAttribute('data-mode', targetScreen);
        if (targetScreen === "timeout") {
            body.setAttribute('data-position', 'middle');
        }else {
            switch (station[1]) {
                case "1":
                    body.setAttribute('data-position', 'right');
                    break;
                case "2":
                    body.setAttribute('data-position', 'middle');
                    break;
                case "3":
                    body.setAttribute('data-position', 'left');
                    break;
            }
        }
    }
}

function handleMatchLoad (data) {
    if (station !== "") {
        let team = data.teams[station];

        $('#teamNameText').setAttribute('data-alliance-bg', station[0]);
        $('#teamRank').setAttribute('data-alliance-bg', station[0]);

        if (team) {
            $('$teamNumber').setAttribute('data-alliance-bg', station[0]);
            $('#teamNumber').textContent = team.id;
            $('#teamNameText').textContent = team.nickname;

            let ranking = data.rankings[team.id];
            if (ranking && data.match.type === 2) {
                $('#teamRank').textContent = ranking;
            }else {
                $('#teamRank').textContent = "";
            }
        }else {
            $('#teamNumber').textContent = "";
            $('#teamNameText').textContent = "";
            $('#teamRank').textContent = "";
        }

        let playoffAlliance = data.match.playoff_red_alliance;
        let offFieldTeams = data.red_off_field_teams;
        if (station[0] === "B") {
            playoffAlliance = data.match.playoff_blue_alliance;
            offFieldTeams = data.blue_off_field_teams;
        }

        if (playoffAlliance > 0) {
            let playoffAllianceInfo = `Alliance ${playoffAlliance}`;
            if (offFieldTeams.length) {
                playoffAllianceInfo += `&emsp; Not on Field: ${offFieldTeams.map(team => team.id).join(", ")}`;
            }
            $('#playoffAllianceInfo').innerHTML = playoffAllianceInfo;
        }else {
            $('#playoffAllianceInfo').textContent = "";
        }
    }
}

function handleArenaStatus (data) {
    let stationStatus = data.alliance_stations[station];
    let blink = false;

    if (stationStatus && stationStatus.bypass) {
        $('#match').setAttribute('data-status', 'bypass');
    }else if (stationStatus) {
        if (!stationStatus.ds_conn || !stationStatus.ds_conn.ds_linked) {
            $('#match').setAttribute('data-status', station[0]);
        }else if (!stationStatus.ds_conn.robot_linked) {
            blink = true;
            if (!blinkInterval) {
                blinkInterval = setInterval(() => {
                    let status = $('#match').getAttribute('data-status');
                    $('#match').setAttribute('data-status', (status === "") ? station[0] : "");
                }, 250);
            }
        }else {
            $('#match').setAttribute('data-status', "");
        }
    }

    if (!blink && blinkInterval) {
        clearInterval(blinkInterval);
        blinkInterval = null;
    }
}

function handleMatchTime (data) {
    translateMatchTime(data, (matchState, matchStateText, countdown) => {
        if (station[0] === "N") {
            matchState = "TELEOP_PERIOD";
        }

        let countdownString = String(countdown % 60);
        if (countdownString.length === 1) {
            countdownString = '0' + countdownString;
        }
        countdownString = Math.floor(countdown / 60) + ':' + countdownString;
        $('#timeRemaining').textContent = countdownString;
        $('#match').setAttribute('data-state', matchState);
    });
}

function handleRealtimeScore (data) {
    $('#redScore').textContent = data.red.score_summary.score - data.red.score_summary.barge_points;
    $('#blueScore').textContent = data.blue.score_summary.score - data.blue.score_summary.barge_points;
}

let urlParams = new URLSearchParams(window.location.search);
station = urlParams.get('station');

websocket = new wsHandler("/api/displays/alliance_station/websocket" + window.location.search, {
    alliance_station_display_mode: (e) => { handleAllianceStationDisplayMode(e.data) },
    arena_status: (e) => { handleArenaStatus(e.data) },
    match_load: (e) => { handleMatchLoad(e.data) },
    match_time: (e) => { handleMatchTime(e.data) },
    match_timing: (e) => { handleMatchTiming(e.data) },
    realtime_score: (e) => { handleRealtimeScore(e.data) }
})