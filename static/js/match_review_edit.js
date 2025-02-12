let editor = new bootstrap.Modal($('#editMatch'));
let resultCache = {};

const generateScoreEditor = (match, result, red) => {
    return `
        <div class="row">
            <table class="table table-striped table-hover table-bordered">
                <thead>
                    <tr>
                        <th>Team</th>
                        <th>${red?match.red1:match.blue1}</th>
                        <th>${red?match.red2:match.blue2}</th>
                        <th>${red?match.red3:match.blue3}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Leave</td>
                        ${result.leave_statuses.map((leave) => {
                            return `
                                <td>
                                    <input name="${red?'red':'blue'}Leave" type="checkbox" ${leave? 'checked' : ''}>
                                </td>
                            `
                        }).join('\n')}
                    </tr>
                    <tr>
                        <td>Bypass</td>
                        ${result.bypass_statuses.map((bypass) => {
                            return `
                                <td>
                                    <input name="${red?'red':'blue'}Bypass" type="checkbox" ${bypass? 'checked' : ''}>
                                </td>
                            `
                        }).join('\n')}
                    </tr>
                    <tr>
                        <td>Cage Deep?</td>
                        ${result.cage_statuses.map((status) => {
                            return `
                                <td>
                                    <input name="${red?'red':'blue'}Cage" type="checkbox" ${status? 'checked' : ''}>
                                </td>
                            `
                        }).join('\n')}
                    </tr>
                    <tr>
                        <td>Endgame</td>
                        ${result.endgame_statuses.map((endgame) => {
                            return `
                                <td>
                                    <select name="${red?'red':'blue'}Endgame" class="form-control" value="${endgame}">
                                        <option value="0">None</option>
                                        <option value="1">Park</option>
                                        <option value="2">Cage Left</option>
                                        <option value="3">Cage Center</option>
                                        <option value="4">Cage Right</option>
                                    </select>
                                </td>
                            `
                        }).join('\n')}
                    </tr>
                    <tr>
                        <th scope="row">Auto Branches</th>
                        <td>Level 2</td>
                        <td>Level 3</td>
                        <td>Level 4</td>
                    </tr>
                    ${result.score_elements.branches_auto.map((branch, index) => {
                        return `
                            <tr>
                                <td>${String.fromCharCode(65 + index)}</td>
                                ${branch.map((coral) => {
                                    return `
                                        <td>
                                            <input name="${red?'red':'blue'}Auto" type="checkbox" ${coral? 'checked' : ''}>
                                        </td>
                                    `
                                }).join('\n')}
                            </tr>
                        `
                    }).join('\n')}
                    <tr>
                        <th scope="row">Total Branches</th>
                        <td>Level 2</td>
                        <td>Level 3</td>
                        <td>Level 4</td>
                    </tr>
                    ${result.score_elements.branches.map((branch, index) => {
                        return `
                            <tr>
                                <td>${String.fromCharCode(65 + index)}</td>
                                ${branch.map((coral) => {
                                    return `
                                        <td>
                                            <input name="${red?'red':'blue'}Branches" type="checkbox" ${coral? 'checked' : ''}>
                                        </td>
                                    `
                                }).join('\n')}
                            </tr>
                        `
                    }).join('\n')}
                </tbody>
            </table>
        </div>
        <div class="row">
            <legend>Trough</legend>
        </div>
        <div class="row">
            <label for="${red?'red':'blue'}TroughAuto" class="col-2 col-form-label">Auto</label>
            <div class="col-4">
                <input id="${red?'red':'blue'}TroughAuto" type="number" class="form-control" value="${result.score_elements.auto_trough_coral}">
            </div>
            <label for="${red?'red':'blue'}TroughTeleop" class="col-2 col-form-label">Teleop</label>
            <div class="col-4">
                <input id="${red?'red':'blue'}TroughTeleop" type="number" class="form-control" value="${result.score_elements.total_trough_coral - result.score_elements.auto_trough_coral}">
            </div>
        </div>
        <div class="row">
            <legend>Processor</legend>
        </div>
        <div class="row">
            <label for="${red?'red':'blue'}ProcessorAuto" class="col-2 col-form-label">Auto</label>
            <div class="col-4">
                <input id="${red?'red':'blue'}ProcessorAuto" type="number" class="form-control" value="${result.score_elements.auto_trough_coral}">
            </div>
            <label for="${red?'red':'blue'}ProcessorTeleop" class="col-2 col-form-label">Teleop</label>
            <div class="col-4">
                <input id="${red?'red':'blue'}ProcessorTeleop" type="number" class="form-control" value="${result.score_elements.total_trough_coral - result.score_elements.auto_trough_coral}">
            </div>
        </div>
        <div class="row">
            <legend>Net</legend>
        </div>
        <div class="row">
            <label for="${red?'red':'blue'}NetAuto" class="col-2 col-form-label">Auto</label>
            <div class="col-4">
                <input id="${red?'red':'blue'}NetAuto" type="number" class="form-control" value="${result.score_elements.auto_trough_coral}">
            </div>
            <label for="${red?'red':'blue'}NetTeleop" class="col-2 col-form-label">Teleop</label>
            <div class="col-4">
                <input id="${red?'red':'blue'}NetTeleop" type="number" class="form-control" value="${result.score_elements.total_trough_coral - result.score_elements.auto_trough_coral}">
            </div>
        </div>
            
    `
}

const openEditor = (id) => {
    getData(`/api/match/review/${id}/edit`)
    .then((data) => {
        console.log(data);
        resultCache = data;
        $('#editorTitle').innerText = data.match.short_name;
        $('#editorContainer').innerHTML = `
            <div class="row justify-content-around">
                <div class="col-5">
                    ${generateScoreEditor(data.match, data.match_result.red_score, true)}
                </div>
                <div class="col-5">
                    ${generateScoreEditor(data.match, data.match_result.red_score, false)}
                </div>
            </div>
        `;
        editor.show();
    })
}

const saveResult = () => {
    let data = {
        match_id: resultCache.match.id,
        play_number: resultCache.match_result.play_number,
        match_type: resultCache.match.type,
        red_score: {
            leave_statuses: Array.from($$('input[name="redLeave"]')).map((leave) => leave.checked),
            bypass_statuses: Array.from($$('input[name="redBypass"]')).map((bypass) => bypass.checked),
            cage_statuses: Array.from($$('input[name="redCage"]')).map((cage) => cage.checked? 1 : 0),
            endgame_statuses: Array.from($$('input[name="redEndgame"]')).map((endgame) => endgame.value),
            score_elements: {
                branches_auto: Array.from($$('input[name="redAuto"]')).map((branch) => branch.checked),
                branches: Array.from($$('input[name="redBranches"]')).map((branch) => branch.checked),
                auto_trough_coral: parseInt($('#redTroughAuto').value),
                total_trough_coral: parseInt($('#redTroughAuto').value) + parseInt($('#redTroughTeleop').value),
                auto_processor_coral: parseInt($('#redProcessorAuto').value),
                teleop_processor_coral: parseInt($('#redProcessorTeleop').value),
                auto_net_coral: parseInt($('#redNetAuto').value),
                teleop_net_coral: parseInt($('#redNetTeleop').value)
            }
        },
        blue_score: {
            leave_statuses: Array.from($$('input[name="blueLeave"]')).map((leave) => leave.checked),
            bypass_statuses: Array.from($$('input[name="blueBypass"]')).map((bypass) => bypass.checked),
            cage_statuses: Array.from($$('input[name="blueCage"]')).map((cage) => cage.checked? 1 : 0),
            endgame_statuses: Array.from($$('input[name="blueEndgame"]')).map((endgame) => endgame.value),
            score_elements: {
                branches_auto: Array.from($$('input[name="blueAuto"]')).map((branch) => branch.checked),
                branches: Array.from($$('input[name="blueBranches"]')).map((branch) => branch.checked),
                auto_trough_coral: parseInt($('#blueTroughAuto').value),
                total_trough_coral: parseInt($('#blueTroughAuto').value) + parseInt($('#blueTroughTeleop').value),
                auto_processor_coral: parseInt($('#blueProcessorAuto').value),
                teleop_processor_coral: parseInt($('#blueProcessorTeleop').value),
                auto_net_coral: parseInt($('#blueNetAuto').value),
                teleop_net_coral: parseInt($('#blueNetTeleop').value)
            }
        },
        red_cards: resultCache.match_result.red_cards,
        blue_cards: resultCache.match_result.blue_cards,
    }
    
    postData(`/api/match/${resultCache.match.id}/edit`, data)
    .then((data) => {
        console.log(data);
        resultCache = {};
        editor.hide();
    })
}