var wsHandler = function (path, events) {
    var handler = this;
    var protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    var url = `${protocol}//${window.location.host}${path}${window.location.search}`;

    if (!events.hasOwnProperty('error')) {
        events.error = function (e) {
            console.error('WebSocket error:', e.data);
        };
    }

    var displayId = new URLSearchParams(window.location.search).get('displayId');

    events.reload = function (e) {
        if (e.data === null || e.data === displayId) {
            location.reload();
        }
    };

    if (!events.hasOwnProperty('displayConfiguration')) {
        events.displayConfiguration = function (e) {
            if (e.data !== window.location.pathname + window.location.search) {
                window.location = e.data;
            }
        };
    }

    this.connect = function () {
        this.websocket = new WebSocket(url);

        this.websocket.onopen = function () {
            console.log('WebSocket connected to Server at ', url);
        };

        this.websocket.onclose = function () {
            console.log('WebSocket disconnected from Server. Retry after 3 seconds...');
            setTimeout(handler.connect, 3000);
        };

        this.websocket.onmessage = function (e) {
            var event = JSON.parse(e.data);
            if (events.hasOwnProperty(event.type)) {
                events[event.type](event);
            }
        };


        window.onbeforeunload = function (e) {
            handler.websocket.close();
        };
    }

    this.send = function (type, data) {
        this.websocket.send(JSON.stringify({
            "type": type,
            "data": data
        }));
    };

    this.connect();
}