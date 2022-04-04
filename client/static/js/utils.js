getRandom = () => {
    return (Math.random() * (78 - 41) + 78).toFixed(3) * 1;
}

function getRandomInRange(from, to, fixed) {
    return (Math.random() * (to - from) + from).toFixed(fixed) * 1;
}


setCurrentPosition = (position) => {
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;
    removeMark(id);
    addMark(id, latitude, longitude, username, MY_COLOR);
}


setFakePosition = () => {
    latitude = getRandomInRange(41, 78, 3);
    longitude = getRandomInRange(19, 169, 3);
}


getFakePosition = (callback) => {
    callback({
        coords: {
            latitude: latitude,
            longitude: longitude,
        },
    });
}
