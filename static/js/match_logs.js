
const typeName = {
    1: 'Practice',
    2: 'Qualification',
    3: 'Playoff'
}

const generateMatches = (matches) => {
    return matches.map((match) => {
        return `
            <tr>
                <td class="bg-${match.color_class}">${match.short_name}</td>
                <td class="bg-${match.color_class}">${match.time}</td>
                <td class="bg-${match.color_class} text-center red-text">
                    ${match.red_teams.map((team, index) => `<a href="/api/match/logs/${match.id}/R${index + 1}/log" target="_blank">${team}</a>`).join('\n')}
                </td>
                <td class="bg-${match.color_class} text-center blue-text">
                    ${match.blue_teams.map((team, index) => `<a href="/api/match/logs/${match.id}/B${index + 1}/log" target="_blank">${team}</a>`).join('\n')}
                </td>
            </tr>
        `
    }).join('\n');
}

const generatePanes = (data) => {
    $(`#tab${typeName[data.current_match_type]}`).classList.add('active');

    return Object.entries(data.matches_by_type).map(([type, matches]) => {
        return `
            <div class="tab-pane fade ${data.current_match_type == type? 'show active' : ''}" id="${typeName[type]}" role="tabpanel" aria-labelledby="tab${typeName[type]}">
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Match</th>
                            <th>Scheduled Time</th>
                            <th class="text-center">Red Alliance</th>
                            <th class="text-center">Blue Alliance</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${generateMatches(matches)}
                    </tbody>
                </table>
            </div>
        `
    }).join('\n');
}

const refreshLogs = () => {
    getData('/api/match/logs')
    .then((data) => {
        $('#tabPaneContainer').innerHTML = generatePanes(data);
    });
}

refreshLogs();