let teamEditModal = new bootstrap.Modal($('#editTeam'));
let teamCache = {};

function parseSettings(settings) {
    $$('[name="wpakey"]').forEach(element => {
        if (settings.network_security_enabled) {
            element.classList.remove('d-none');
        }
    });
}

function createRows(teams) {
    teamCache = teams.map(team => {
        return { [team.id]: team }
    }).reduce((acc, val) => Object.assign(acc, val), {});

    let tableHTML = `${teams.map(team => {
        if (team != null) {
            return `<tr id="team-${team.id}">
                <td>${team.id}</td>
                <td>${team.name}</td>
                <td>${team.nickname}</td>
                <td>${team.school_name}</td>
                <td>${team.city}, ${team.state_prov}, ${team.country}</td>
                <td>${team.rookie_year}</td>
                <td>${team.robot_name}</td>
                <td class="text-center">
                    <button class="btn btn-primary btn-sm" onclick="editTeam('${team.id}')"><i class="bi-pencil-square"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="deleteTeam('${team.id}')"><i class="bi-trash"></i></button>
                </td>
            </tr>`
        }else{
            return ''
        }
    }).join("\n")}
    `
    return tableHTML
}

function uploadTeams() {
    let team_area = $('#teamNumbers');
    if (team_area.value == "") {
        return
    }
    let team_ids = team_area.value.split("\n").filter(Boolean).map(Number);
    postData('/api/setup/teams', {
        'team_ids': team_ids
    })
    .then(data => $('#tableContainer').innerHTML += createRows(data))
    .catch(error => console.error(error))
    team_area.value = ""
}

function deleteTeam(team_id) {
    try {
        deleteData(`/api/setup/teams/${team_id}`)
        .then(response => getData('/api/setup/teams'))
        .then(teams => $('#tableContainer').innerHTML = createRows(teams))
        
    }catch (error) {
        console.error(error);
    }
}


function editTeam(team_id) {
    $('#teamId').value = teamCache[team_id].id;
    $('#teamName').value = teamCache[team_id].name;
    $('#teamNickname').value = teamCache[team_id].nickname;
    $('#teamSchoolName').value = teamCache[team_id].school_name;
    $('#teamCity').value = teamCache[team_id].city;
    $('#teamStateProv').value = teamCache[team_id].state_prov;
    $('#teamCountry').value = teamCache[team_id].country;
    $('#teamRookieYear').value = teamCache[team_id].rookie_year;
    $('#teamRobotName').value = teamCache[team_id].robot_name;
    $('#teamAccomplishments').value = teamCache[team_id].accomplishments;
    $('#teamWpakey').value = teamCache[team_id].wpakey;
    teamEditModal.show();
}

function saveTeam() {
    postData('/api/setup/teams/' + $('#teamId').value, {
        'id': $('#teamId').value,
        'name': $('#teamName').value,
        'nickname': $('#teamNickname').value,
        'school_name': $('#teamSchoolName').value,
        'city': $('#teamCity').value,
        'state_prov': $('#teamStateProv').value,
        'country': $('#teamCountry').value,
        'rookie_year': $('#teamRookieYear').value,
        'robot_name': $('#teamRobotName').value,
        'accomplishments': $('#teamAccomplishments').value,
        'wpakey': $('#teamWpakey').value
    }).then(response => {
        $('#team-' + response.id).innerHTML = `
            <td>${response.id}</td>
            <td>${response.name}</td>
            <td>${response.nickname}</td>
            <td>${response.school_name}</td>
            <td>${response.city}, ${response.state_prov}, ${response.country}</td>
            <td>${response.rookie_year}</td>
            <td>${response.robot_name}</td>
            <td class="text-center">
                <button class="btn btn-primary btn-sm" onclick="editTeam('${response.id}')"><i class="bi-pencil-square"></i></button>
                <button class="btn btn-danger btn-sm" onclick="deleteTeam('${response.id}')"><i class="bi-trash"></i></button>
            </td>
        `
        teamCache[response.id] = response;
        teamEditModal.hide();
    }).catch(error => console.error(error))
}

function truncateTeams() {
    try {
        deleteData(`/api/setup/teams/clear`)
        .then(response => {
            $('#tableContainer').innerHTML = ''
        })
    }catch (error) {
        console.error(error);
    }
}

function generateWpaKeys(all) {
    try {
        getData(`/api/setup/teams/generate_wpa_keys?all=${all}`)
        .then(response => getData('/api/setup/teams'))
        .then(teams => $('#tableContainer').innerHTML = createRows(teams))
    }catch (error) {
        console.error(error);
    }
}

getData('/api/setup/settings')
.then(settings => parseSettings(settings))

getData('/api/setup/teams')
.then(teams => {
    $('#tableContainer').innerHTML = createRows(teams)
})