init = () => {
    initMap();
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(handlePosition, chooseFakePositioning);
    } else {
        chooseFakePositioning();
    }
}

chooseFakePositioning = () => {
    console.log('Не получается узнать настоящее местоположение');
    setFakePosition();
    generateLocationButton.style.display = 'block';
    useFakeLocation = true;
    getFakePosition(handlePosition);
}


handlePosition = (position) => {
    setCurrentPosition(position);
    connection = new Connection(onOpen, onMessage, onClose, onError);
}


onMessage = (msg) => {
    let event = JSON.parse(msg.data);
    const kind = event['kind'];
    const payload = event['payload'];
    console.log(`new event with kind ${kind} and payload ${JSON.stringify(payload)}`);
    if (kind === INITIAL) {
        onFullyConnected(payload);
    } else if (kind === ADD) {
        addMark(payload['id'], payload['latitude'], payload['longitude'], payload['name'], OTHER_COLOR);
    } else if (kind === MOVE) {
        removeMark(payload['id']);
        addMark(payload['id'], payload['latitude'], payload['longitude'], payload['name'], OTHER_COLOR);
    } else if (kind === REMOVE) {
        removeMark(payload['id']);
    } else {
        console.log(`unsupported event kind ${kind}, data ${payload}`)
    }
}

onFullyConnected = (payload) => {
    id = payload['id'];
    connection.push(CONNECT_EVENT, {
        id: id,
        name: username,
        latitude: latitude,
        longitude: longitude,
    });

    for (let user of payload['users']) {
        addMark(user['id'], user['latitude'], user['longitude'], user['name'], OTHER_COLOR);
    }
    if (useFakeLocation) {
        setInterval(() => getFakePosition(ping, (e) => console.log(e)), 1000);
    } else {
        setInterval(() => navigator.geolocation.getCurrentPosition(ping, (e) => console.log(e)), 1000);
    }

}

ping = (position) => {
    if (!run) return;
    removeMark('initial');
    setCurrentPosition(position);
    console.log(`ping with latitude: ${latitude}, longitude: ${longitude}`);
    connection.push(PING_EVENT, {
        id: id,
        latitude: latitude,
        longitude: longitude,
    });
}


onOpen = () => {
    console.log('ws connection opened');
}


onClose = () => {
    console.log('ws connection closed');
    connection.push(
        DISCONNECT_EVENT,
        {
            id: id,
        }
    );
    run = false;
}


onError = (e) => {
    console.log(`connection closed with error ${e}`);
    run = false;
}

generateLocationButton.addEventListener('click', setFakePosition);