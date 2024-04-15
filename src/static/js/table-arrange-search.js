/*jshint esversion: 9 */

/* global console*/

var sortOrder = []; // Store sorting order for each column

function sortTable(columnIndex, tableName) {
    "use strict";
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.querySelector(tableName);
    switching = true;

    if (!sortOrder[columnIndex] || sortOrder[columnIndex] === 'desc') {
        sortOrder[columnIndex] = 'asc';
    } else {
        sortOrder[columnIndex] = 'desc';
    }

    while (switching) {
        switching = false;
        rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("td")[columnIndex];
            y = rows[i + 1].getElementsByTagName("td")[columnIndex];

            if (sortOrder[columnIndex] === 'asc') {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            } else {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            }
        }

        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }

    // Remove arrow indicators from all headers
    var headers = document.querySelectorAll(tableName + "th");
    headers.forEach(function (header) {
        header.classList.remove('asc', 'desc');
    });

    // Add arrow indicator to the sorted column header
    var currentHeader = document.querySelector(tableName + "th:nth-child(" + (columnIndex + 1) + ")");
    if (sortOrder[columnIndex] === 'asc') {
        currentHeader.classList.add('asc');
    } else {
        currentHeader.classList.add('desc');
    }
}

function filterTable(tableName) {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("searchInput" + tableName);
    filter = input.value.toLowerCase();
    table = document.querySelector(tableName);
    tr = table.getElementsByTagName("tr");

    for (i = 1; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td");
        for (var j = 0; j < td.length; j++) {
            if (td[j]) {
                txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toLowerCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                    break;
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    }
}
