const renewLowerThird = () => {
    getData("/api/setup/lower_thirds")
    .then(lower_thirds => {
        let endHTML = `
            <div class="row mt-1 mb-3">
                <div class="col-6">
                    <input type="hidden" id="Id0" value="" />
                    <input type="text" class="form-control mb-1" id="topText0" placeholder="Top Text" />
                    <input type="text" class="form-control" id="bottomText0" placeholder="Bottom Text" />
                </div>
                <div class="col-6">
                    <button type="button" class="btn btn-primary mb-1" onclick="saveLowerThird('0')">Save</button>
                </div>
            </div>
        `;

        let lowerThirdsHTML = lower_thirds.map(lower_third => {
            return `
                <div class="row mt-1 mb-3">
                    <div class="col-6">
                        <input type="hidden" id="Id${lower_third.id}" value="${lower_third.id}" />
                        <input type="text" class="form-control mb-1" value="${lower_third.top_text}" id="topText${lower_third.id}" placeholder="Top Text" />
                        <input type="text" class="form-control" value="${lower_third.bottom_text}" id="bottomText${lower_third.id}" placeholder="Bottom Text" />
                    </div>
                    <div class="col-6">
                        <button type="button" class="btn btn-primary mb-1" onclick="saveLowerThird('${lower_third.id}')">Save</button>
                        <button type="button" class="btn btn-success mb-1" onclick="showLowerThird('${lower_third.id}')">Show</button>
                        <button type="button" class="btn btn-primary mb-1" onclick="reorderLowerThird('${lower_third.id}', true)"><i class="bi-arrow-up"></i></button>
                        <button type="button" class="btn btn-success mb-1" onclick="showLowerThirdOnly('${lower_third.id}')">Show Only Thirds</button>
                        <br />
                        <button type="button" class="btn btn-danger" onclick="deleteLowerThird('${lower_third.id}')">Delete</button>
                        <button type="button" class="btn btn-secondary" onclick="hideLowerThird('${lower_third.id}')">Hide</button>
                        <button type="button" class="btn btn-primary" onclick="reorderLowerThird('${lower_third.id}', false)"><i class="bi-arrow-down"></i></button>
                    </div>
                </div>
            `
        }).join("\n");

        $('#lowerThirdsContainer').innerHTML = lowerThirdsHTML + endHTML;
    })
}

function constructData(lowerThirdId) {
    return {
        id: parseInt($('#Id' + lowerThirdId).value),
        top_text: $('#topText' + lowerThirdId).value,
        bottom_text: $('#bottomText' + lowerThirdId).value,
    }
}

function saveLowerThird(lowerThirdId) {
    websocket.send('save_lower_third', constructData(lowerThirdId));
    renewLowerThird();
}

function deleteLowerThird(lowerThirdId) {
    websocket.send('delete_lower_third', constructData(lowerThirdId));
    renewLowerThird();
}

function showLowerThird(lowerThirdId) {
    websocket.send('show_lower_third', constructData(lowerThirdId));
    renewLowerThird();
}

function showLowerThirdOnly(lowerThirdId) {
    websocket.send('show_lower_third', constructData(lowerThirdId));
    $('input[name=audienceDisplay][value=blank]').checked = true;
    setAudienceDisplay();
    renewLowerThird();
}

function hideLowerThird(lowerThirdId) {
    websocket.send('hide_lower_third', constructData(lowerThirdId));
    renewLowerThird();
}

function reorderLowerThird(lowerThirdId, moveup) {
    websocket.send('reorder_lower_third', {
        id: parseInt($('#Id' + lowerThirdId).value),
        move_up: moveup,
    });
    renewLowerThird();
}

const setAudienceDisplay = function () {
    websocket.send('set_audience_display', $('input[name=audienceDisplay]:checked').value);
}

const handleAudienceDisplayMode = function (data) {
    $('input[name=audienceDisplay]:checked').checked = false;
    $(`input[name=audienceDisplay][value=${data.data}]`).checked = true;
}

let websocket = new wsHandler('/api/setup/lower_thirds/websocket', {
    audience_display_mode: handleAudienceDisplayMode,
})

renewLowerThird();