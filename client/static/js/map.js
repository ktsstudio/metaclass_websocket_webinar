initMap = () => {
    map = new ymaps.Map("map", {
        center: [55.76, 37.64],
        zoom: 7
    });
}

let marks = new Map();

addMark = (id, latitude, longitude, name = username, color = MY_COLOR) => {
    let mark = new ymaps.Placemark([latitude, longitude], {
        balloonContentHeader: name,
    }, {
        preset: `islands#${color}CircleDotIcon`,
    });
    map.geoObjects.add(mark);
    marks.set(id, mark);
}

removeMark = (id) => {
    let mark = marks.get(id);
    map.geoObjects.remove(mark);
    marks.delete(id);
}