/*jshint esversion: 9 */
/* global console*/
/* global L*/

/* global map*/
let busIdToMarker = {};
let dirTemp = 'DOWN';

function updateDirection(dir) {
    "use strict";
    if (dirTemp === dir) {
        return 0;
    }

    if (dir === "UP") {
        document.getElementsByClassName('bus-icon')[0].style.backgroundImage = "url('/static/images/UP.png')";
    } else {
        document.getElementsByClassName('bus-icon')[0].style.backgroundImage = "url('/static/images/DOWN.png')";
    }
    dirTemp = dir;
}

function removeRouteFromMap(busId) {
    "use strict";
    var layers = busIdToMarker[busId];
    console.log(layers)
    if (layers) {
        // Remove bus marker from the map
        if (layers.busMarker) {
            map.removeLayer(layers.busMarker);
        }

        // Remove stage markers from the map
        if (layers.stageMarkers && layers.stageMarkers.length > 0) {
            layers.stageMarkers.forEach(function (marker) {
                map.removeLayer(marker);
            });
        }

        // Remove route polyline from the map
        if (layers.routePoly) {
            map.removeLayer(layers.routePoly);
        }

        // Remove shadow polyline from the map
        if (layers.routeShadow) {
            map.removeLayer(layers.routeShadow);
        }

        // Remove the layers from the busIdToMarker object
        delete busIdToMarker[busId];
    }
}

function showRouteWithMarkers(busId, stagePoints, routePoints) {
    "use strict";
    if (busIdToMarker.hasOwnProperty(busId)) {
        return 0;
    }
    console.log(busIdToMarker.hasOwnProperty(busId));
    var markersArray = [];
    for (var i = 0; i < stagePoints.length; i++) {
        var marker = L.marker(stagePoints[i].stageCoord).addTo(map);
        markersArray.push(marker);
        // Add popups to markers (optional)
        marker.bindPopup(stagePoints[i].stageName, {
            autoClose: false,
            closeOnClick: false
        });
    }

// Custom divIcon for the rotating bus marker
    const busIcon = L.divIcon({
        className: 'bus-icon',
        iconSize: [32, 32], // Set the size of the icon
    });

// Add the bus marker with the custom divIcon
    const busMarker = L.marker([0, 0], {icon: busIcon, rotationAngle: 45}).addTo(map);

//busMarker.bindPopup("<strong>Hello world!</strong><br />I am a popup.", {maxWidth: 500});

// Initialize an empty polyline for the bus's trail
    var routePoly = L.polyline(routePoints, {color: 'blue', weight: 10}).addTo(map);
    var shadowPolyline = L.polyline(routePoints, {color: 'black', weight: 14, opacity: 0.3}).addTo(map);
    busIdToMarker[busId] = {
        "busMarker": busMarker,
        "stageMarkers": markersArray,
        "routePoly": routePoly,
        "routeShadow": shadowPolyline
    };
// Move the shadow polyline to the back
    shadowPolyline.bringToBack();
//const trail = L.polyline([], {color: 'blue', weight: 4}).addTo(map);

}

// Function to update the bus marker's position and rotation and log distance
let prevLocation = {};

function updateBusMarker(busId, location) {
    "use strict";
    if (!(prevLocation.hasOwnProperty(busId))) {
        rotateMapToLocation(busId, L.latLng(location));
        busIdToMarker[busId].busMarker.setLatLng(L.latLng(location));
        prevLocation[busId] = location;
        return 0;
    }
    const latLng = L.latLng(location);

    //rotateMapToLocation(latLng);
    busIdToMarker[busId].busMarker.setLatLng(latLng);
    //trail.addLatLng(latLng);

    // Add the current position to the bus's trail

    // Calculate the angle between two points to set the rotation
    const angle = Math.atan2(location[1] - prevLocation[busId][1], location[0] - prevLocation[busId][0]);
    const degrees = (angle * 180) / Math.PI;

// Assuming `busMarker` is a Leaflet marker
    //busIdToMarker[busId].busMarker.setRotationAngle(degrees);
    //console.log(busIdToMarker.busId.getLatLng())
    //const distance = map.distance(busIdToMarker.busId.getLatLng(), L.latLng(arr[arr.length - 1].stageCoord));

}

function rotateMapToLocation(busId, targetLatLng) {
    "use strict";
    if (targetLatLng) {
        // Calculate bearing between current marker position and target location
        var bearing = getBearing(busIdToMarker[busId].busMarker.getLatLng(), targetLatLng);

        // Smoothly rotate the map
        map.setView(targetLatLng, 17, {
            animate: true,
            duration: 1,
            pan: {
                animate: true,
                duration: 1,
                easeLinearity: 0.5,
            },
            zoom: {
                animate: true,
                duration: 1,
            },
            bearing: bearing,
        });
    }
}

// Helper function to calculate bearing between two points
function getBearing(prevPoint, nextPoint) {
    "use strict";
    var x = Math.cos(nextPoint.lat) * Math.sin(nextPoint.lng - prevPoint.lng);
    var y = Math.cos(prevPoint.lat) * Math.sin(nextPoint.lat) -
        Math.sin(prevPoint.lat) * Math.cos(nextPoint.lat) * Math.cos(nextPoint.lng - prevPoint.lng);
    var bearing = Math.atan2(x, y);
    return (bearing * (180 / Math.PI) + 360) % 360;
}