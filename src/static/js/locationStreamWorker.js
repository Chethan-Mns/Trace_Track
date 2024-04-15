/*jshint esversion: 9 */
/* global self*/
/* global EventSource*/
/* global console*/
/* global postMessage*/

let source;
self.addEventListener("message", function (e) {
    "use strict";
    // the passed-in data is available via e.data
    console.log(e.data.mode);

    function connect(busIds) {
        source = new EventSource("https://vehispot.onrender.com/users/locationStreamMultiple/" + "?busIds=" + busIds + "&token=" + e.data.token);

        source.onopen = function (event) {
            console.log("SSE connection established.");
        };

        source.onerror = function (event) {
            if (event.target.readyState === EventSource.CLOSED) {
                console.error("SSE connection closed.");
            } else {
                console.error("SSE connection error:", event);
                // Retry connection after some time
                // Retry after 5 seconds (adjust as needed)
            }
        };

        source.onmessage = function (event) {
            const recievedData = JSON.parse(event.data);
            console.log(recievedData);
            if (recievedData.event === "update") {
                postMessage(recievedData);
            }
        };
    }

    if (e.data.mode === "start") {
        connect(e.data.busIds);
    }// Connect initially
    else if (e.data.mode === "stop") {
        if (source) {
            source.close();
            console.log("SSE connection closed.");
        }
    }
}, false);