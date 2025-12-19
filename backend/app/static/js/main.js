// Main JS for Websocket and common functions

let socket;
const statusBadge = document.querySelector('#connection-status .badge');

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/web-client-${Math.floor(Math.random() * 1000)}`;

    socket = new WebSocket(wsUrl);

    socket.onopen = function (e) {
        console.log("Connection established");
        statusBadge.className = 'badge bg-success';
        statusBadge.innerText = 'Connected';
    };

    socket.onmessage = function (event) {
        // console.log(`Data received from server: ${event.data}`);
        try {
            const data = JSON.parse(event.data);
            // Dispatch a custom event so pages can listen
            const customEvent = new CustomEvent('ws-message', { detail: data });
            window.dispatchEvent(customEvent);
        } catch (e) {
            console.log("Received non-JSON message:", event.data);
        }
    };

    socket.onclose = function (event) {
        if (event.wasClean) {
            console.log(`Connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
            console.log('Connection died');
        }
        statusBadge.className = 'badge bg-danger';
        statusBadge.innerText = 'Disconnected';

        // Try to reconnect in 5 seconds
        setTimeout(connectWebSocket, 5000);
    };

    socket.onerror = function (error) {
        console.log(`[error] ${error.message}`);
    };
}

document.addEventListener("DOMContentLoaded", function () {
    connectWebSocket();
});
