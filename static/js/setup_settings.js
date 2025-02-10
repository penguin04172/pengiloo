function parseSettings(data) {
    $('#eventName').value = data.name;
    $$('input[name="playoffType"]')[data.playoff_type].checked = true;
    $('#numPlayoffAlliances').value = data.num_playoff_alliances;
    $('#numPlayoffAlliances').disabled = data.playoff_type == 0;
    $(`input[name="selectionRound2Order"][value="${data.selection_round_2_order}"]`).checked = true;
    $(`input[name="selectionRound3Order"][value="${data.selection_round_3_order}"]`).checked = true;
    $('#selectionShowUnpickedTeams').checked = data.selection_show_unpicked_teams;
    $('#tbaDownloadEnabled').checked = data.tba_download_enabled;
    $('#tbaPublishingEnabled').checked = data.tba_publishing_enabled;
    $('#tbaPublishingArea').classList.toggle('d-none', !data.tba_publishing_enabled);
    $('#tbaEventCode').value = data.tba_event_code;
    $('#tbaSecretId').value = data.tba_secret_id;
    $('#tbaSecret').value = data.tba_secret;
    $('#nexusEnabled').checked = data.nexus_enabled;
    $('#adminPassword').value = data.admin_password;
    $('#networkSecurityEnabled').checked = data.network_security_enabled;
    $('#apAddress').value = data.ap_address;
    $('#apPassword').value = data.ap_password;
    $('#apChannel').value = data.ap_channel;
    $('#switchAddress').value = data.switch_address;
    $('#switchPassword').value = data.switch_password;
    $('#plcAddress').value = data.plc_address;
    $('#teamSignRed1Id').value = data.team_sign_red_1_id;
    $('#teamSignRed2Id').value = data.team_sign_red_2_id;
    $('#teamSignRed3Id').value = data.team_sign_red_3_id;
    $('#teamSignRedTimerId').value = data.team_sign_red_timer_id;
    $('#teamSignBlue1Id').value = data.team_sign_blue_1_id;
    $('#teamSignBlue2Id').value = data.team_sign_blue_2_id;
    $('#teamSignBlue3Id').value = data.team_sign_blue_3_id;
    $('#teamSignBlueTimerId').value = data.team_sign_blue_timer_id;
    $('#blackmagicAddress').value = data.blackmagic_address;
    $('#autoDurationSec').value = data.auto_duration_sec;
    $('#pauseDurationSec').value = data.pause_duration_sec;
    $('#teleopDurationSec').value = data.teleop_duration_sec;
    $('#warningRemainingDurationSec').value = data.warning_remaining_duration_sec;
    $('#autoBonusCoralThreshold').value = data.auto_bonus_coral_threshold;
    $('#coralBonusNumThreshold').value = data.coral_bonus_num_threshold;
    $('#coralBonusLevelThresholdWithoutCoop').value = data.coral_bonus_level_threshold_without_coop;
    $('#coralBonusLevelThresholdWithCoop').value = data.coral_bonus_level_threshold_with_coop;
    $('#bargeBonusPointThreshold').value = data.barge_bonus_point_threshold;
}

function uploadSettings() {
    const settings = {
        name: $('#eventName').value,
        playoff_type: $('input[name="playoffType"]:checked').value,
        num_playoff_alliances: $('#numPlayoffAlliances').value,
        selection_round_2_order: $('input[name="selectionRound2Order"]:checked').value,
        selection_round_3_order: $('input[name="selectionRound3Order"]:checked').value,
        selection_show_unpicked_teams: $('#selectionShowUnpickedTeams').checked,
        tba_download_enabled: $('#tbaDownloadEnabled').checked,
        tba_publishing_enabled: $('#tbaPublishingEnabled').checked,
        tba_event_code: $('#tbaEventCode').value,
        tba_secret_id: $('#tbaSecretId').value,
        tba_secret: $('#tbaSecret').value,
        nexus_enabled: $('#nexusEnabled').checked,
        admin_password: $('#adminPassword').value,
        network_security_enabled: $('#networkSecurityEnabled').checked,
        ap_address: $('#apAddress').value,
        ap_password: $('#apPassword').value,
        ap_channel: $('#apChannel').value,
        switch_address: $('#switchAddress').value,
        switch_password: $('#switchPassword').value,
        plc_address: $('#plcAddress').value,
        team_sign_red_1_id: $('#teamSignRed1Id').value,
        team_sign_red_2_id: $('#teamSignRed2Id').value,
        team_sign_red_3_id: $('#teamSignRed3Id').value,
        team_sign_red_timer_id: $('#teamSignRedTimerId').value,
        team_sign_blue_1_id: $('#teamSignBlue1Id').value,
        team_sign_blue_2_id: $('#teamSignBlue2Id').value,
        team_sign_blue_3_id: $('#teamSignBlue3Id').value,
        team_sign_blue_timer_id: $('#teamSignBlueTimerId').value,
        blackmagic_address: $('#blackmagicAddress').value,
        auto_duration_sec: $('#autoDurationSec').value,
        pause_duration_sec: $('#pauseDurationSec').value,
        teleop_duration_sec: $('#teleopDurationSec').value,
        warning_remaining_duration_sec: $('#warningRemainingDurationSec').value,
        auto_bonus_coral_threshold: $('#autoBonusCoralThreshold').value,
        coral_bonus_num_threshold: $('#coralBonusNumThreshold').value,
        coral_bonus_level_threshold_without_coop: $('#coralBonusLevelThresholdWithoutCoop').value,
        coral_bonus_level_threshold_with_coop: $('#coralBonusLevelThresholdWithCoop').value,
        barge_bonus_point_threshold: $('#bargeBonusPointThreshold').value
    };
    fetch("/api/setup/settings", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    }).then(response => response.json())
    .then(data => parseSettings(data))
    .catch(error => console.error(error));
}
