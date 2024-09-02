// Grab the chat, grip it
// Then read the chat, may God give me strength
// Try and make it used in streamlabs



// Identify variables
var tmi = require('tmi.js');
var say = require('say');

// BOT connection options
var options = {
    options: {
        debug: false
    },
    connection: {
        cluster: "aws",
        reconnect: true
    },
    identity: {
        username: "", // Bot username
        password: "" // oautho, bot account
    },
    channels: [""] // Channel you want to go to
}

var client = new tmi.client(options);
client.connect()

client.on("chat", funtion (channel, userstate, message, self) {
    say.speak(message);
});