function parseSettings(settings) {
    $$('[name="wpakey"]').forEach(element => {
        if (settings.network_security_enabled) {
            element.classList.remove('d-none');
        }
    });
}

function createRows(teams) {
    let tableHTML = `${teams.map(team => {
        if (team != null) {
            return `<tr>
                <td>${team.id}</td>
                <td>${team.name}</td>
                <td>${team.nickname}</td>
                <td>${team.school_name}</td>
                <td>${team.city}, ${team.state_prov}, ${team.country}</td>
                <td>${team.rookie_year}</td>
                <td>${team.robot_name}</td>
                <td class="text-center">
                    <button class="btn btn-primary btn-sm"><i class="bi-pencil-square"></i></button>
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