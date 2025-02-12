let fieldsChanged = false;

function configureDisplay(displayId) {
    var configurationMap = {}
    $('#displayConfiguration' + displayId).value.split('&').map((param) => {
        let [key, value] = param.split('=');
        configurationMap[key] = value;
    });

    fieldsChanged = false;
    websocket.send('configure_display', {
        id: displayId,
        nickname: $('#displayNickname' + displayId).value,
        type: parseInt($('#displayType' + displayId).value),
        configuration: configurationMap
    });
}

function undoChanges() {
    window.location.reload();
}

function reloadDisplay(displayId) {
    websocket.send('reload_display', displayId);
}

function reloadAllDisplays() {
    websocket.send('reload_all_displays', null);
}

function markChanged(element) {
    fieldsChanged = true;
    element.set-attribute("data-changed", true);
}

function handleDisplayConfiguration(data) {
    if (fieldsChanged) {
        return
    }

    let displaysHTML = Object.entries(data).map((displayId, display) => {
        return `
            <tr ${display.connection_count? '' : 'class="table-danger"'}>
                <td>${display.display_configuration.id}</td>
                <td>${display.connection_count}</td>
                <td>${display.ip_address}</td>
                <td><input type="text" id="displayNickname${display.display_configuration.id}" size="30" oninput="markChanged(this);" /></td>
                <td>
                    <select id="displayType${display.display_configuration.id}" onchanged="markChanged(this);">
                        ${displayTypeNames.map((type, typeName) => `<option value="${type}">${typeName}</option>`).join('')}
                    </select>
                </td>
                <td>
                    <input type="text" id="displayConfiguration${display.display_configuration.id}" size="50" oninput="markChanged(this);" />
                </td>
                <td>
                    <button type="button" class="btn btn-primary btn-sm" title="Save Changes" onclick="configureDisplay('${display.display_configuration.id}')">
                        <i class="bi-check-lg"></i>
                    </button>
                    <button type="button" class="btn btn-danger btn-sm" title="Undo Changes" onclick="undoChanges()">
                        <i class="bi-arrow-left"></i>
                    </button>
                    <button type="button" class="btn btn-success btn-sm" title="Reload Display" onclick="reloadDisplay('${display.display_configuration.id}')">
                        <i class="bi-arrow-clockwise"></i>
                    </button>
                </td>
            </tr>
        `
    }).join('\n');

    $('#displaysContainer').innerHTML = displaysHTML;
}

let displayTypeNames = getData('/api/setup/displays').then(data => data);
let websocket = new wsHandler("/api/setup/displays/websocket", {
    display_configuration: (e) => handleDisplayConfiguration(e.data)
})