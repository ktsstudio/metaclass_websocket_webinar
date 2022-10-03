// globals
let connection;
let map;
let path;
let run = true;
let generateLocationButton = document.getElementById('generate-location')
let useFakeLocation = false;

// user
let username;
let id = 'initial';
let latitude, longitude;

const MY_COLOR = 'green';
const OTHER_COLOR = 'red';


// server
const INITIAL = 'initial'
const ADD = 'add'
const MOVE = 'move'
const REMOVE = 'remove'

// client
const CONNECT_EVENT = 'connect';
const DISCONNECT_EVENT = 'disconnect';
const PING_EVENT = 'ping';


