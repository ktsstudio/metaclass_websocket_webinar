init = () => {
    username = prompt('Введи свое имя', 'Аноним');
    ymaps.ready(initMap);
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(handlePosition);
    } else {
        alert('Извини, но похоже твой браузер не поддерживает геолокацию')
    }
}

handlePosition = (position) => {
    setCurrentPosition(position);
    connection = new Connection(onOpen, onMessage, onClose, onError);
}


setCurrentPosition = (position) => {
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;
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
    addMark(id, latitude, longitude);
    for (let user in payload['users']) {
        addMark(user['id'], user['latitude'], user['longitude'], user['name'], OTHER_COLOR);
    }
    setInterval(() => navigator.geolocation.getCurrentPosition(ping, (e) => console.log(e)), 5000);

}

ping = (position) => {
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;
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
    )
}


onError = (e) => {
    console.log(`connection closed with error ${e}`)
}