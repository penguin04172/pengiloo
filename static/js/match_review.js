
const generateMatches = (matches) => {
    return matches.map((match) => {
        return `
            <tr>
                <td class="bg-${match.color_class}">${match.short_name}</td>
                <td class="bg-${match.color_class}">${match.time}</td>
                <td class="bg-${match.color_class} text-center red-text">
                    ${match.red_teams.map((team) => team).join(', ')}
                </td>
                <td class="bg-${match.color_class} text-center blue-text">
                    ${match.blue_teams.map((team) => team).join(', ')}
                </td>
                <td class="bg-${match.color_class} text-center red-text">
                    ${match.is_complete? match.red_score : '-'}
                </td>
                <td class="bg-${match.color_class} text-center blue-text">
                    ${match.is_complete? match.blue_score : '-'}
                </td>
                <td class="bg-${match.color_class} text-center">
                    <button type="button" class="btn btn-primary" onclick="openEditor('${match.id}')">
                        Edit
                    </button>
                </td>
            </tr>
        `
    }).join('');
}

const typeName = {
    1: 'Practice',
    2: 'Qualification',
    3: 'Playoff'
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
                            <th class="text-center">Red Score</th>
                            <th class="text-center">Blue Score</th>
                            <th class="text-center">Actions</th>
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

const renewMatchReview = (data) => {
    $('#tabPaneContainer').innerHTML = generatePanes(data);
    
}

const refreshMatchReview = () => {
    getData('/api/match/review')
    .then((data) => {
        renewMatchReview(data);
    })
}

refreshMatchReview();