/*jshint esversion: 9 */

/* global console*/
/* global getData*/
/* global postData*/

// Get the modal
var modal = document.getElementById("myModal");


// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal
// When the user clicks on <span> (x), close the modal
span.onclick = function () {
    "use strict";
    modal.style.display = "none";
};

// {#// When the user clicks anywhere outside the modal, close it#}
// {#window.onclick = function (event) {#}
// {#    if (event.target == modal) {#}
// {#        modal.style.display = "none";#}
// {#    }#}
// {# };#}

// Function to open the modal
async function openModal(type) {
    "use strict";
    await getData('https://vehispot.onrender.com/users/getFormStructure/?type=' + type).then(data => {
        data = data[type + 'DataStructure'];
        document.getElementById('addEditForm').innerHTML = '';
        for (var i = 0; i < data.length; i++) {
            var entr = `<label for="name">${data[i]}:</label>
                            <input type="text"  name="${data[i]}" placeholder="Enter your ${data[i]}">`;
            document.getElementById('addEditForm').insertAdjacentHTML('beforeend', entr);
        }
        document.getElementById('addEditForm').insertAdjacentHTML('beforeend', `<input type="hidden" data-action="new" value="${type}" id="formType">`);
        document.getElementById('addEditForm').insertAdjacentHTML('beforeend', `<input type="submit" hidden>`);
        document.getElementById('saveData').setAttribute('onclick', `saveData('${type}')`)
        if (document.getElementById('editStages'))
            document.getElementById('editStages').remove();
    });

    modal.style.display = "block";
}

// Function to close the modal
function closeModal() {
    modal.style.display = "none";
}

// Function to save data (dummy function for demonstration)
document.getElementById('addEditForm').addEventListener('submit', (e) => {
    e.preventDefault();
    console.log('hello');
    console.log(document.getElementById('formType').dataset.action)
    if (document.getElementById('formType').dataset.action === "new")
        saveData(document.getElementById('formType').value);
    else
        updateData(document.getElementById('formType').value);
})

function saveData(type) {
    "use strict";
    console.log(type);
    const formD = document.getElementById('addEditForm');
    const formO = new FormData(formD);
    postData('https://vehispot.onrender.com/users/saveData/?type=' + type, Object.fromEntries(formO)).then(data => {
        console.log(data)
        // Get the table body
        var table = document.getElementsByClassName(type + "Table")[0]
        var tableBody = table.getElementsByTagName('tbody')[0];

        // Check if headers exis

        // If headers do not exist, create header row
        if (!tableBody) {
            var tb = document.createElement('tbody');
            var headerRow = document.createElement('tr');

            // Create headers based on keys from the data
            var i = 0;
            for (var key in data.savedData) {
                if (data.savedData.hasOwnProperty(key)) {
                    var th = document.createElement('th');
                    th.setAttribute("onclick", `sortTable(${i},'.${type}Table')`);
                    th.setAttribute("class", type + "Tableth asc");
                    th.textContent = key;
                    headerRow.appendChild(th);
                }
                i++;
            }
            var th = document.createElement('th');
            th.textContent = "Actions";
            headerRow.appendChild(th);

            // Append header row to the table
            tb.appendChild(headerRow);
            table.appendChild(tb);
            tableBody = tb;
        }

        // Create a new row for values
        var valueRow = document.createElement('tr');

        // Populate cells with values from the data
        for (var key in data.savedData) {
            if (data.savedData.hasOwnProperty(key)) {
                var td = document.createElement('td');
                td.textContent = data.savedData[key];
                valueRow.appendChild(td);
            }
        }
        valueRow.innerHTML += `<td class="action-buttons">
                            <button class="edit-button" onclick="editAction('${type}','${data.id}')"><span
                                    class="las la-edit"></span>Edit</button>
                            <button class="delete-button" onclick="deleteAction('${type}','${data.id}')">Delete</button>
                        </td>`;

        // Append value row to the table
        tableBody.appendChild(valueRow);
    })
        .catch(error => console.error('Error fetching data:', error));
    closeModal();
}

async function editAction(type, id) {
    "use strict";
    document.getElementById('addEditForm').innerHTML = '';
    await getData('https://vehispot.onrender.com/users/getData/?type=' + type + '&fid=' + id).then(async data => {
        console.log(data);
        for (const [key, value] of Object.entries(data)) {
            var entr;
            if (key === "allotedBusId") {
                await getData('https://vehispot.onrender.com/users/getNonAllotatedData/?type=bus' + "&checkFor=" + capitalizeFirstLetter(type)).then(nonAllotData => {
                    console.log(nonAllotData);
                    entr = `<label for="name">${key}:</label><select name="${key}"><option selected value="${value}">${value}</option>`
                    for (var i = 0; i < nonAllotData.length; i++) {
                        entr += `<option value="${nonAllotData[i].busId}">${nonAllotData[i].busNumber}</option>`;
                    }
                    entr += `</select>`;
                });
            } else if (key === "allotedDriverId") {
                await getData('https://vehispot.onrender.com/users/getNonAllotatedData/?type=driver').then(nonAllotData => {
                    console.log(nonAllotData);
                    entr = `<label for="name">${key}:</label><select name="${key}"><option selected value="${value}">${value}</option>`
                    for (var i = 0; i < nonAllotData.length; i++) {
                        entr += `<option value="${nonAllotData[i].driverId}">${nonAllotData[i].driverName}</option>`;
                    }
                    entr += `</select>`;
                });
            } else if (key === "allotedDeviceId") {
                await getData('https://vehispot.onrender.com/users/getNonAllotatedData/?type=device').then(nonAllotData => {
                    console.log(nonAllotData);
                    entr = `<label for="name">${key}:</label><select name="${key}"><option selected value="${value}">${value}</option>`
                    for (var i = 0; i < nonAllotData.length; i++) {
                        entr += `<option value="${nonAllotData[i].deviceId}">${nonAllotData[i].deviceId}</option>`;
                    }
                    entr += `</select>`;
                });
            } else if (key === "allotedRouteId") {
                await getData('https://vehispot.onrender.com/users/getNonAllotatedData/?type=route').then(nonAllotData => {
                    console.log(nonAllotData);
                    entr = `<label for="name">${key}:</label><select name="${key}"><option selected value="${value}">${value}</option>`
                    for (var i = 0; i < nonAllotData.length; i++) {
                        entr += `<option value="${nonAllotData[i].routeId}">${nonAllotData[i].areaName}</option>`;
                    }
                    entr += `</select>`;
                });
            } else {
                if (key === "busId" || key === "routeId" || key === "deviceId" || key === "driverId")
                    entr = `<label for="name">${key}:</label>
                            <input type="text"  name="${key}" value="${value}" placeholder="Enter your ${key}" readonly>`;
                else
                    entr = `<label for="name">${key}:</label>
                            <input type="text"  name="${key}" value="${value}" placeholder="Enter your ${key}">`;
            }
            console.log(entr);
            document.getElementById('addEditForm').insertAdjacentHTML('beforeend', entr);
        }
        document.getElementById('addEditForm').insertAdjacentHTML('beforeend', `<input type="hidden" value="${type}" data-action="edit" id="formType">`);
        document.getElementById('addEditForm').insertAdjacentHTML('beforeend', `<input type="submit" hidden>`);
        document.getElementById('saveData').setAttribute('onclick', `updateData('${type}')`)
        const editStagesBtn = document.getElementById('editStages');
        if (type === 'route') {
            if (!(editStagesBtn))
                document.getElementById('footer-btn').insertAdjacentHTML('afterbegin', `<button type="button" class="btn" id="editStages" onclick="editStages('${id}')">Edit Stages</button>`)
        } else {
            if (editStagesBtn) {
                editStagesBtn.remove();
            }
        }
        modal.style.display = "block";

    });
}


function updateData(type) {
    "use strict";
    const formD = document.getElementById('addEditForm');
    const formO = new FormData(formD);
    postData('https://vehispot.onrender.com/users/updateData/?type=' + type, Object.fromEntries(formO)).then(data => {
        location.reload();
    });
}

function deleteAction(type, id) {
    getData('https://vehispot.onrender.com/users/deleteData/?type=' + type + "&dId=" + id).then(data => {
        if (data.status) {
            console.log(this);
            this.document.activeElement.parentNode.parentElement.remove();
        }
    });
}

function editStages(rid) {
    "use strict";
    window.location.href = '/createRouteWithStages/?rid=' + rid;
}
