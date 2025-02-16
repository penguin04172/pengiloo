const matchTypeName = {
    0: 'Test',
    1: 'Practice',
    2: 'Qualification',
    3: 'Playoff',
}

const matchTypeTest = 0;
const matchTypePractice = 1;
const matchTypeQualification = 2;
const matchTypePlayoff = 3;

const matchStates = {
    0: 'PRE_MATCH',
    1: 'START_MATCH',
    2: 'WARMUP_PERIOD',
    3: 'AUTO_PERIOD',
    4: 'PAUSE_PERIOD',
    5: 'TELEOP_PERIOD',
    6: 'POST_MATCH',
    7: 'TIMEOUT_ACTIVE',
    8: 'POST_TIMEOUT',
}

let matchTiming;

const handleMatchTiming = (data) => {
    matchTiming = data
}

const translateMatchTime = (data, callback) => {
    var matchStateText;

    switch (matchStates[data.match_state]) {
        case 'PRE_MATCH':
            matchStateText = 'PRE-MATCH';
            break;
        case 'START_MATCH':
        case 'WARMUP_PERIOD':
            matchStateText = 'WARMUP';
            break;
        case 'AUTO_PERIOD':
            matchStateText = 'AUTONOMOUS';
            break;
        case 'PAUSE_PERIOD':
            matchStateText = 'PAUSE';
            break;
        case 'TELEOP_PERIOD':
            matchStateText = 'TELEOPERATED';
            break;
        case 'POST_MATCH':
            matchStateText = 'POST-MATCH';
            break;
        case 'TIMEOUT_ACTIVE':
        case 'POST_TIMEOUT':
            matchStateText = 'TIMEOUT';
            break;
    }

    callback(matchStates[data.match_state], matchStateText, getCountdown(data.match_state, data.match_time_sec));
}


const getCountdown = (matchState, matchTimeSec) => {
    switch (matchStates[matchState]) {
        case 'PRE_MATCH':
        case 'START_MATCH':
        case 'WARMUP_PERIOD':
            return matchTiming.auto_duration_sec;
        case 'AUTO_PERIOD':
            return matchTiming.warmup_duration_sec + matchTiming.auto_duration_sec - matchTimeSec;
        case 'TELEOP_PERIOD':
            return matchTiming.warmup_duration_sec + matchTiming.auto_duration_sec + matchTiming.pause_duration_sec + matchTiming.teleop_duration_sec - matchTimeSec;
        case 'TIMEOUT_ACTIVE':
            return matchTiming.timeout_duration_sec - matchTimeSec;
        default:
            return 0;
    }
}

const getCountdownString = (countdownSec) => {
    let countdownString = String(countdownSec % 60);
    if (countdownString.length === 1) {
        countdownString = '0' + countdownString;
    }
    
}