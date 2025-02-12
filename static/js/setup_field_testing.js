const renewMatchSounds = (data) => {
    let body = data.map((sound) => {
        return `
            <p>
                <button type="button" class="btn btn-sm btn-primary" onclick="playSound('${sound.name}')">
                    <i class="bi-play-fill"></i>&nbsp;&nbsp;${sound.name.toUpperCase()}
                </button>
            </p>
        `
    }).join('\n');

    $('#soundsContainer').innerHTML = body;
}

const playSound = (soundName) => {
    websocket.send('play_sound', soundName);
}

getData('/api/setup/field_testing')
.then(data => renewMatchSounds(data))

let websocket = new wsHandler('/api/setup/field_testing/websocket', {

})