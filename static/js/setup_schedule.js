let blockMatches = {};
let numTeams = 0;

const generateBlockHTML = (blockNumber, matchSpacingMinSec) => {
    return `
        <div class="card bg-body-tertiary mb-3" id="block${blockNumber}">
            <div class="card-header">
                <div class="row justify-content-between">
                    <legend class="col-6">Block ${blockNumber}</legend>
                    <button type="button" class="btn-close col-1" onclick="deleteBlock('${blockNumber}')"></button>
                </div>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <label for="startTime${blockNumber}" class="col-lg-4 col-form-label">Start Time</label>
                    <div class="input-group col-lg-8" id="startTimePicker${blockNumber}">
                        <input type="text" class="form-control" id="startTime${blockNumber}" onchange="updateBlock('${blockNumber}')" />
                        <span class="input-group-text">
                            <i class="bi bi-calendar"></i>
                        </span>
                    </div>
                </div>
                <div class="row mb-3">
                    <label for="endTime${blockNumber}" class="col-lg-6 col-form-label">End Time</label>
                    <div class="input-group col-lg-6" id="endTimePicker${blockNumber}">
                        <input type="text" class="form-control" id="endTime${blockNumber}" onchange="updateBlock('${blockNumber}')" />
                        <span class="input-group-text">
                            <i class="bi bi-calendar"></i>
                        </span>
                    </div>
                </div>
                <div class="row mb-3">
                    <label for="matchSpacingMinSec${blockNumber}" class="col-lg-4 col-form-label">Cycle Time</label>
                    <div class="col-lg-8">
                        <input type="text" class="form-control" name="name" id="matchSpacingMinSec${blockNumber}" placeholder="6:00" onchange="updateBlock('${blockNumber}')" value="${matchSpacingMinSec}" />
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-4">Match Count: <span id="numMatches${blockNumber}"></span></div>
                    <div class="col-8">Actual end time: <span id="actualEndTime${blockNumber}"></span></div>
                </div>
            </div>
        </div>
    `;
}

const generateScheduleHTML = (matches) => {
    return matches.map(match => {
        return `
            <tr>
                <td>${match.long_name}</td>
                <td>${moment(match.scheduled_time, "YYYY-MM-DDTHH:mm:ss").format("YYYY-MM-DD hh:mm A")}</td>
            </tr>
        `;
    }).join('\n');
}

const generateFirstMatchesHTML = (matches) => {
    return Object.entries(matches).map(([team, match]) => {
        return `
            <tr>
                <td>${team}</td>
                <td>${match}</td>
            </tr>
        `;
    }).join('\n');
}

function addBlock(startTime, numMatches, matchSpacingSec) {
    let lastBlockNumber = getLastBlockNumber();
    if (!startTime) {
        if (Object.keys(blockMatches).length === 0){
            matchSpacingSec = 360;
            startTime = moment().add(1, 'hour').startOf('hour')
        }else {
            let lastStartTime = moment($('#startTime' + lastBlockNumber).value, 'YYYY-MM-DD hh:mm:ss A');
            let lastNumMatches = blockMatches[lastBlockNumber];
            matchSpacingSec = getMatchSpacingSec(lastBlockNumber);
            startTime = lastStartTime.add(lastNumMatches * matchSpacingSec, 'seconds');
        }
        numMatches = 10;
    }

    let endTime = startTime.clone().add(numMatches * matchSpacingSec, 'seconds');
    lastBlockNumber += 1;
    let matchSpacingMinSec = moment.utc(matchSpacingSec * 1000).format('m:ss');

    $('#blockContainer').insertAdjacentHTML('beforeend', '\n' + generateBlockHTML(lastBlockNumber, matchSpacingMinSec));
    newDateTimePicker('startTimePicker' + lastBlockNumber, startTime.toDate());
    newDateTimePicker('endTimePicker' + lastBlockNumber, endTime.toDate());
    updateBlock(lastBlockNumber);
}

function updateBlock(blockNumber) {
    let startTime = moment($('#startTime' + blockNumber).value, 'YYYY-MM-DD hh:mm:ss A');
    let endTime = moment($('#endTime' + blockNumber).value, 'YYYY-MM-DD hh:mm:ss A');
    let matchSpacingSec = getMatchSpacingSec(blockNumber);

    let numMatches = Math.floor(endTime.diff(startTime) / (matchSpacingSec * 1000));
    let actualEndTime = moment(startTime + numMatches * matchSpacingSec * 1000).format('hh:mm:ss A');

    blockMatches[blockNumber] = numMatches;
    if (matchSpacingSec === "" || isNaN(numMatches) || numMatches < 0) {
        numMatches = "";
        actualEndTime = "";
        blockMatches[blockNumber] = 0;
    }
    $('#numMatches' + blockNumber).innerText = numMatches;
    $('#actualEndTime' + blockNumber).innerText = actualEndTime;

    updateStats();
}

function updateStats() {
    let totalNumMatches = 0;
    Object.entries(blockMatches).forEach(([k, v]) => {
        totalNumMatches += v;
    })

    let matchesPerTeam = Math.floor(totalNumMatches * 6 / numTeams);
    let numExcessMatches = totalNumMatches - Math.ceil(matchesPerTeam * numTeams / 6);
    let nextLevelMatches = Math.ceil((matchesPerTeam + 1) * numTeams / 6) - totalNumMatches;


    $('#totalNumMatches').innerText = totalNumMatches;
    $('#matchesPerTeam').innerText = matchesPerTeam;
    $('#numExcessMatches').innerText = numExcessMatches;
    $('#nextLevelMatches').innerText = nextLevelMatches;
}

function deleteBlock(blockNumber) {
    delete blockMatches[blockNumber];
    $('#block' + blockNumber).remove();
    updateStats();
}

function generateSchedule() {
    postData('/api/setup/schedule/generate?match_type=' + $('input[name="matchType"]:checked').value, {
        num_schedule_blocks: Object.keys(blockMatches).length,
        schedule_blocks: Object.entries(blockMatches).map(([blockNumber, numMatches]) => {
            return {
                start_time: moment($('#startTime' + blockNumber).value, 'YYYY-MM-DD hh:mm:ss A').format("YYYY-MM-DDTHH:mm:ss"),
                num_matches: parseInt($('#numMatches' + blockNumber).innerText),
                match_spacing_sec: getMatchSpacingSec(blockNumber),
            };
        }),
    })
    .then(data => renewSchedules(data))
    .catch(err => console.error(err));
    
}

function saveSchedule() {
    postData('/api/setup/schedule/save?match_type=' + $('input[name="matchType"]:checked').value, {
    })
    .then(() => refreshSchedules())
    .catch(err => console.error(err));
}

function getMatchSpacingSec(blockNumber) {
    let matchSpacingMinSec = $('#matchSpacingMinSec' + blockNumber).value.split(':');
    return parseInt(matchSpacingMinSec[0]) * 60 + parseInt(matchSpacingMinSec[1]);
}

function getLastBlockNumber() {
    let max = 0;

    Object.entries(blockMatches).forEach((k, v) => {
        let number = parseInt(k);
        if (number > max) {
            max = number;
        }
    })

    return max;
}

const renewSchedules = (data) => {
    numTeams = data.num_teams;
    $('#blockContainer').innerHTML = '';
    blockMatches = {};

    data.schedule_blocks.forEach((block, index) => {
        addBlock(moment(block.start_time, "YYYY-MM-DDTHH:mm:ss"), block.num_matches, block.match_spacing_sec);
    });

    if (data.schedule_blocks.length === 0) {
        addBlock();
    }

    $('#scheduleContainer').innerHTML = generateScheduleHTML(data.matches);
    $('#firstMatchesContainer').innerHTML = generateFirstMatchesHTML(data.team_first_matches);

}

const refreshSchedules = () => {
    getData(`/api/setup/schedule?match_type=${$('input[name="matchType"]:checked').value}`)
    .then(data => renewSchedules(data))
    .catch(err => console.error(err));
}

refreshSchedules();