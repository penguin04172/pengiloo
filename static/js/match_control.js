let websocket;
let scoreIsReady;
let isReplay;
const lowBatteryThreshold = 8;
let confirmCommitModal = new bootstrap.Modal($('#corfirmCommitResults'))


const loadMatch = (matchId) => {
    websocket.send("load_match", { match_id: matchId });
}

const showResult = (matchId) => {
    websocket.send("show_result", { match_id: matchId });
}

const substituteTeams = () => {
    const teams = {
        red1: getTeamNumber('R1'),
        red2: getTeamNumber('R2'),
        red3: getTeamNumber('R3'),
        blue1: getTeamNumber('B1'),
        blue2: getTeamNumber('B2'),
        blue3: getTeamNumber('B3'),
    }

    websocket.send("substitute_teams", teams);
}

const toggleBypass = (station) => {
    websocket.send("toggle_bypass", { station: station });
}

const startMatch = () => {
    websocket.send("start_match", {
        mute_match_sounds: $('#muteMatchSounds').checked,
    });
}

const abortMatch = () => {
    websocket.send("abort_match");
}

const signalReset = () => {
    websocket.send("signal_reset");
}

const commitResults = () => {
    websocket.send("commit_results");
}

const discardResults = () => {
    websocket.send("discard_results");
}

const showOverlay = () => {
    $('input[name=audienceDisplayMode][value=intro]').checked = true;
    setAudienceDisplay();
    $('#showOverlay').disabled = true;
}

const showFinalScore = function() {
    $("input[name=audienceDisplay][value=score]").checked = true;
    setAudienceDisplay();
    $("#showFinalScore").disabled = true;
}
  
const setAudienceDisplay = () => {
    websocket.send("set_audience_display", $('input[name=audienceDisplay]:checked').value);
}

const setAllianceStationDisplay = () => {
    websocket.send("set_alliance_station_display", $('input[name=allianceStationDisplay]:checked').value);
}

const startTimeout = () => {
    const duration = $('#timeoutDuration').value.split(':');
    let durationSec = parseFloat(duration[0]);
    if (duration.length > 1) {
        durationSec = durationSec * 60 + parseFloat(duration[1]);
    }
    websocket.send("start_timeout", { duration_sec: durationSec});
}

const confirmCommit = () => {
    if (isReplay || !scoreIsReady) {
        $('#confirmCommitReplay').style.display = isReplay?'block':'none';
        $('#confirmCommitNotReady').style.display = !scoreIsReady?'block':'none';
        confirmCommitModal.show();
    }else {
        commitResults();
    }
}

const setTestMatchName = () => {
    websocket.send("set_test_match_name", { name: $('#testMatchName').value});
}

const getTeamNumber = (station) => {
    const teamId = $(`#status${station} .team-number`).value.trim();
    return teamId ? parseInt(teamId) : 0;
}

const handleArenaStatus = (data) => {
    // console.log(data);
    Object.entries(data.alliance_stations).forEach(([station, stationStatus]) => {
        const wifiStatus = stationStatus.wifi_status;
        $('#status' + station + ' .radio-status').innerText = wifiStatus.team_id;

        if (stationStatus.ds_conn) {
            ds_conn = stationStatus.ds_conn;
            $('#status' + station + ' .ds-status').setAttribute('data-status-ok', ds_conn.ds_linked);

            if (ds_conn.ds_linked) {
                $('#status' + station + ' .ds-status').innerText = wifiStatus.mbits.toFixed(2).toString() + 'Mb';
            } else {
                $('#status' + station + ' .ds-status').innerText = "";
            }

            const robotOkay = ds_conn.battery_voltage > lowBatteryThreshold && ds_conn.robot_linked;
            $('#status' + station + ' .robot-status').setAttribute('data-status-ok', robotOkay);
            if (stationStatus.ds_conn.seconds_since_last_robot_packet > 1 && stationStatus.ds_conn.seconds_since_last_ds_packet < 1000) {
                $('#status' + station + ' .robot-status').innerText = stationStatus.ds_conn.seconds_since_last_robot_packet.toFixed();
            }else {
                $('#status' + station + ' .robot-status').innerText = ds_conn.battery_voltage.toFixed(1).toString() + 'V';
            }
        }else {
            $('#status' + station + ' .ds-status').setAttribute('data-status-ok', "");
            $('#status' + station + ' .robot-status').setAttribute('data-status-ok', "");
            $('#status' + station + ' .robot-status').innerText = "";
        }

        const expectedTeamId = stationStatus.team ? stationStatus.team.id : 0;
        let radioStatus = 0;
        if (wifiStatus.teamId === expectedTeamId) {
            if (wifiStatus.radio_linked || stationStatus.ds_conn?.robot_linked) {
                radioStatus = 2;
            }else {
                radioStatus = 1;
            }
        }
        $('#status' + station + ' .radio-status').setAttribute('data-status-tertiary', radioStatus);

        if (stationStatus.e_stop) {
            $('#status' + station + ' .bypass-status').setAttribute('data-status-ok', false);
            $('#status' + station + ' .bypass-status').innerText = 'ES';
        }else if (stationStatus.a_stop) {
            $('#status' + station + ' .bypass-status').setAttribute('data-status-ok', true);
            $('#status' + station + ' .bypass-status').innerText = 'AS';
        }else if (stationStatus.bypass) {
            $('#status' + station + ' .bypass-status').setAttribute('data-status-ok', false);
            $('#status' + station + ' .bypass-status').innerText = 'B';
        }else {
            $('#status' + station + ' .bypass-status').setAttribute('data-status-ok', true);
            $('#status' + station + ' .bypass-status').innerText = '';
        }
    });

    switch (matchStates[data.match_state]) {
        case "PRE_MATCH":
            $('#startMatch').disabled = !data.can_start_match;
            $('#abortMatch').disabled = true;
            $('#signalReset').disabled = false;
            $('#commitResults').disabled = true;
            $('#discardResults').disabled = true;
            $('#showOverlay').disabled = false;
            $('#startTimeout').disabled = false;
            break;
        case "START_MATCH":
        case "WARMUP_PERIOD":
        case "AUTO_PERIOD":
        case "PAUSE_PERIOD":
        case "TELEOP_PERIOD":
            $('#showOverlay').disabled = true;
            $('#introRadio').disabled = true;
            $('#showFinalScore').disabled = true;
            $('#scoreRadio').disabled = true;
            $('#startMatch').disabled = true;
            $('#abortMatch').disabled = false;
            $('#signalReset').disabled = false;
            $('#fieldResetRadio').disabled = true;
            $('#commitResults').disabled = true;
            $('#editResults').disabled = true;
            $('#startTimeout').disabled = true;
            break;
        case "POST_MATCH":
            $('#showOverlay').disabled = true;
            $('#introRadio').disabled = true;
            $('#showFinalScore').disabled = true;
            $('#scoreRadio').disabled = true;
            $('#startMatch').disabled = true;
            $('#abortMatch').disabled = true;
            $('#signalReset').disabled = false;
            $('#fieldResetRadio').disabled = false;
            $('#commitResults').disabled = false;
            $('#discardResults').disabled = false;
            $('#editResults').disabled = true;
            $('#startTimeout').disabled = true;
            break;
        case "TIMEOUT_ACTIVE":
            $('#showOverlay').disabled = true;
            $('#introRadio').disabled = true;
            $('#showFinalScore').disabled = false;
            $('#scoreRadio').disabled = false;
            $('#startMatch').disabled = true;
            $('#abortMatch').disabled = false;
            $('#signalReset').disabled = true;
            $('#fieldResetRadio').disabled = false;
            $('#commitResults').disabled = true;
            $('#discardResults').disabled = true;
            $('#editResults').disabled = true;
            $('#startTimeout').disabled = true;
            break;
        case "POST_TIMEOUT":
            $('#showOverlay').disabled = false;
            $('#introRadio').disabled = false;
            $('#showFinalScore').disabled = false;
            $('#scoreRadio').disabled = false;
            $('#startMatch').disabled = true;
            $('#abortMatch').disabled = true;
            $('#signalReset').disabled = true;
            $('#fieldResetRadio').disabled = false;
            $('#commitResults').disabled = true;
            $('#discardResults').disabled = true;
            $('#editResults').disabled = true;
            $('#startTimeout').disabled = true;
            break;
    }

    $('#accessPointStatus').setAttribute('data-status', data.AccessPointStatus);
    $('#switchStatus').setAttribute('data-status', data.SwitchStatus);

    if (data.plc_is_healthy) {
        $('#plcStatus').innerText = "Connected";
        $('#plcStatus').setAttribute('data-ready', true);
    }else {
        $('#plcStatus').innerText = "Not Connected";
        $('#plcStatus').setAttribute('data-ready', false);
    }
    $('#fieldEStop').setAttribute('data-ready', !data.field_e_stop);
    
    // Object.entries(data.plc_armor_block_statuses).forEach(([name, status]) => {
    //     $('#plc' + name + 'Status').setAttribute('data-ready', status);
    // });
}

const updateMatchList = (data) => {
    let matchListHTML = `
        <b class="btn btn-primary" onclick="loadMatch(0)">Load Test Match</b>
        <ul class="nav nav-tabs mt-4">
            <li><a href="#Practice" class="nav-link ${data.current_match_type === 1 ? 'active' : ''}" data-bs-toggle="tab">Practice</a></li>
            <li><a href="#Qualification" class="nav-link ${data.current_match_type === 2 ? 'active' : ''}" data-bs-toggle="tab">Qualification</a></li>
            <li><a href="#Playoff" class="nav-link ${data.current_match_type === 3 ? 'active' : ''}" data-bs-toggle="tab">Playoff</a></li>
        </ul>
        <div class="tab-content">
            ${Object.entries(data.matches_by_type).map(([type, matches]) => {
                return `
                    <div class="match-list tab-pane ${data.current_match_type === parseInt(type) ? 'show active' : ''}" id="${matchTypeName[type]}">
                        <table class="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th>Match</th>
                                    <th>Time</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${matches.map(match => {
                                    return `
                                        <tr>
                                            <td class="bg-${match.color_class}">${match.short_name}</td>
                                            <td class="bg-${match.color_class}">${match.time}</td>
                                            <td class="bg-${match.color_class} nowrap">
                                                <b class="btn btn-primary btn-sm" onclick="loadMatch(${match.id})">Load</b>
                                                ${match.status !== 0 ? `<b class="btn btn-primary btn-sm" onclick="showResult(${match.id})">Show Result</b>` : ''}
                                            </td>
                                        </tr>
                                    `
                                }).join('\n')}
                            </tbody>
                        </table>
                    </div>
                `
            }).join('\n')}
        </div>
    `
    $('#matchListContainer').innerHTML = matchListHTML;
}

const handleMatchLoad = (data) => {
    isReplay = data.is_replay;

    getData('/api/match/control/load')
        .then(data => {
            updateMatchList(data);
        });

    $('#matchName').innerText = data.match.long_name;
    $('#testMatchName').value = data.match.long_name;
    $('#testMatchSettings').style.display = data.match.type === 0 ? 'block' : 'none';
    Object.entries(data.teams).forEach(([station, team]) => {
        const teamId = $(`#status${station} .team-number`);
        teamId.value = team ? team.id : "";
        teamId.disabled = !data.allow_substitution;
    });

    $('#playoffRedAllianceInfo').innerHTML = formatPlayoffAllianceInfo(data.match.playoff_red_alliance, data.red_off_field_teams);
    $('#playoffBlueAllianceInfo').innerHTML = formatPlayoffAllianceInfo(data.match.playoff_blue_alliance, data.blue_off_field_teams);

    $('#substituteTeams').disabled = true;
    $('#showOverlay').disabled = false;
    $('#introRadio').disabled = false;
    $('#muteMatchSounds').checked = false;
}

const handleMatchTime = (data) => {
    translateMatchTime(data, (matchState, matchStateText, countdownSec) => {
        let matchStateElement = $('#matchState');
        if (matchStateElement) {
            matchStateElement.textContent = matchStateText;
        }

        let matchTimeElement = $('#matchTime');
        if (matchTimeElement) {
            matchTimeElement.textContent = countdownSec;
        }

    })
}

const handleRealtimeScore = (data) => {
    $('#redScore').textContent = data.red.score_summary.score;
    $('#blueScore').textContent = data.blue.score_summary.score;
}

const handleScorePosted = (data) => {
    let matchName = data.match.long_name;
    if (matchName) {
        $('#showFinalScore').disabled = false;
        $('#scoreRadio').disabled = false;
    }else {
        matchName = "None";
    }

    $('#savedMatchName').innerHTML = matchName;
}

const handleAudienceDisplayMode = (data) => {
    $('input[name=audienceDisplay]:checked').checked = false;
    $(`input[name=audienceDisplay][value=${data}]`).checked = true;
}

const handleScoringStatus = (data) => {
    console.log(data);
    scoreIsReady = data.referee_score_ready && data.red_score_ready && data.blue_score_ready;
    $('#refereeScoringStatus').setAttribute('data-ready', data.referee_score_ready);
    $('#redScoringStatus').textContent = `Red Scoring: ${data.num_red_scoring_panels_ready}/${data.num_red_scoring_panels}`;
    $('#blueScoringStatus').textContent = `Blue Scoring: ${data.num_blue_scoring_panels_ready}/${data.num_blue_scoring_panels}`;
    $('#redScoringStatus').setAttribute('data-ready', data.red_score_ready);
    $('#blueScoringStatus').setAttribute('data-ready', data.blue_score_ready);
}

const handleAllianceStationDisplayMode = (data) => {
    $('input[name=allianceStationDisplay]:checked').checked = false;
    $(`input[name=allianceStationDisplay][value=${data}]`).checked = true;
}

const handleEventStatus = (data) => {
    if (data.cycle_time === "") {
        $('#cycleTimeMessage').textContent = "Last Cycle Time: N/A";
    }else {
        $('#cycleTimeMessage').textContent = `Last Cycle Time: ${data.cycle_time}`;
    }
    $('#earlyLateMessage').textContent = data.early_late_message;
}

const formatPlayoffAllianceInfo = (allianceNumber, offFieldTeams) => {
    if (allianceNumber === 0) {
        return "";
    }

    let allianceInfo = `<b>Alliance ${allianceNumber}:</b>`;
    if (offFieldTeams.length > 0) {
        allianceInfo += ` (not on field: ${offFieldTeams.map(team => team.id).join(", ")})`;
    }
    return allianceInfo;
}

const tooltipTriggerList = $$('[data-bs-toggle="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(element => new bootstrap.Tooltip(element));
websocket = new wsHandler(
    '/api/match/control/websocket', {
        alliance_station_display_mode: (e) => { handleAllianceStationDisplayMode(e.data) },
        arena_status: (e) => { handleArenaStatus(e.data) },
        audience_display_mode: (e) => { handleAudienceDisplayMode(e.data) },
        event_status: (e) => { handleEventStatus(e.data) },
        match_load: (e) => { handleMatchLoad(e.data) },
        match_time:(e) => { handleMatchTime(e.data) },
        match_timing: (e) => { handleMatchTiming(e.data) },
        realtime_score: (e) => { handleRealtimeScore(e.data) },
        score_posted: (e) => { handleScorePosted(e.data) },
        scoring_status: (e) => { handleScoringStatus(e.data) },
    }
);