function renewAwards() {
    getData("/api/setup/awards")
    .then(awards => {
        let initHTML = 
        `
            <div class="row mb-3">
                <div class="col-8">
                    <input type="hidden" name="id" value="0" />
                    <div class="row mb-2">
                        <label for="awardName0" class="col-4 col-form-label">Award Name</label>
                        <div class="col-8">
                            <input type="text" class="form-control" id="awardName0" name="awardName" />
                        </div>
                    </div>
                    <div class="row mb-2">
                        <label for="teamId0" class="col-4 col-form-label">Team Awarded</label>
                        <div class="col-8">
                            <select class="form-select" id="teamId0" name="teamId" value="${teams[0].id}">
                                <option value="0">No Team</option>
                                ${teams.map(team => `<option value="${team.id}">${team.id} - ${team.nickname}</option>`).join("\n")}
                            </select>
                        </div>
                    </div>
                    <div class="row mb-2">
                        <label for="personName0" class="col-4 col-form-label">Person Awarded</label>
                        <div class="col-8">
                            <input type="text" class="form-control" id="personName0" name="personName" />
                        </div>
                    </div>
                </div>
                <div class="col-4">
                    <button type="button" class="btn btn-primary"  onclick="saveAward(0)">Save</button>
                </div>
            </div>

        `
        let awardsHTML = awards.map(award => {
            return `
                <div class="row mb-3">
                    <div class="col-8">
                        <input type="hidden" name="id" value="${award.id}" />
                        <div class="row mb-2">
                            <label for="awardName${award.id}" class="col-4 col-form-label">Award Name</label>
                            <div class="col-8">
                                <input type="text" class="form-control" id="awardName${award.id}" name="awardName" value="${award.award_name}" />
                            </div>
                        </div>
                        <div class="row mb-2">
                            <label for="teamId${award.id}" class="col-4 col-form-label">Team Awarded</label>
                            <div class="col-8">
                                <select class="form-select" id="teamId${award.id}" name="teamId" value="${award.team_id}">
                                    <option value="0">No Team</option>
                                    ${teams.map(team => `<option value="${team.id}" ${team.id==award.team_id?'selected':''}>${team.id} - ${team.nickname}</option>`).join("\n")}
                                </select>
                            </div>
                        </div>
                        <div class="row mb-2">
                            <label for="personName${award.id}" class="col-4 col-form-label">Person Awarded</label>
                            <div class="col-8">
                                <input type="text" class="form-control" id="personName${award.id}" name="personName" value="${award.person_name}" />
                            </div>
                        </div>
                    </div>
                    <div class="col-4">
                        <button type="button" class="btn btn-primary" onclick="saveAward('${award.id}')">Save</button>
                        <button type="button" class="btn btn-danger" onclick="deleteAward('${award.id}')">Delete</button>
                    </div>
                </div>
            `
        }).join("\n")

        $('#awardsContainer').innerHTML = initHTML + awardsHTML
    })
}

function saveAward(id) {
    let award = {
        "id": id == 0 ? null : parseInt(id),
        "award_name": $('#awardName' + id).value,
        "team_id": parseInt($('#teamId' + id).value),
        "person_name": $('#personName' + id).value
    };
    console.log(award);

    postData("/api/setup/awards", award)
    .then(data => {
        renewAwards()
    })
}

function deleteAward(id) {
    deleteData("/api/setup/awards/" + id)
    .then(data => {
        renewAwards()
    })
}