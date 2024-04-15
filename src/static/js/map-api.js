/*jshint esversion: 9 */

/* global console*/

let map;

function loadMap() {
    if (map)
        return 0;
    map = L.map('map').setView([14.028572109658956, 80.0218235993725], 15);
    const openStreetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 20,
    }).addTo(map);
    const googleSatellite = L.tileLayer('https://{s}.google.com/vt?lyrs=y&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
    });

    const googleStreets = L.tileLayer('https://{s}.google.com/vt?lyrs=m&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
    });

    const baseMaps = {
        "OpenStreetMap": openStreetMap,
        "Google Streets": googleStreets,
        "Google Satellite": googleSatellite
    };
    L.control.layers(baseMaps).addTo(map);
}