class Connection {
    constructor(onOpen, onMessage, onClose, onError) {
        if (path === '${CONNECT_PATH}') {
            path = 'ws://localhost:8000/connect';
        }
        this.connection = new WebSocket(path);
        this.connection.onmessage = onMessage;
        this.connection.onclose = onClose;
        this.connection.onerror = onError;
    }

    push = (kind, data) => {
        this.connection.send(JSON.stringify({kind: kind, payload: data}));
    }
}


