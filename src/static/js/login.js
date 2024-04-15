/*jshint esversion: 9 */

/* global console*/

// Function to set a cookie
function setCookie(cookieName, cookieValue, expirationDays) {
    "use strict";
    const d = new Date();
    d.setTime(d.getTime() + (expirationDays * 24 * 60 * 60 * 1000));
    const expires = "expires=" + d.toUTCString();
    document.cookie = cookieName + "=" + cookieValue + ";" + expires + ";path=/";
}

// Function to get a cookie by name
function getCookie(cookieName) {
    "use strict";
    const name = cookieName + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i];
        while (cookie.charAt(0) == ' ') {
            cookie = cookie.substring(1);
        }
        if (cookie.indexOf(name) == 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    return "";
}

function sign_up() {
    "use strict";
    document.getElementById('loginForm').reset();
    document.getElementById('formType').value = 'signup';
    var inputs = document.querySelectorAll('.input_form_sign');
    document.querySelectorAll('.ul_tabs > li')[0].className = "";
    document.querySelectorAll('.ul_tabs > li')[1].className = "active";

    for (var i = 0; i < inputs.length; i++) {
        if (i == 2) {

        } else {
            document.querySelectorAll('.input_form_sign')[i].className = "input_form_sign d_block";
        }
    }

    setTimeout(function () {
        for (var d = 0; d < inputs.length; d++) {
            document.querySelectorAll('.input_form_sign')[d].className = "input_form_sign d_block active_inp";
        }


    }, 100);
    document.querySelector('.link_forgot_pass').style.opacity = "0";
    document.querySelector('.link_forgot_pass').style.top = "-5px";
    document.querySelector('.rememberMe').style.opacity = "0";
    document.querySelector('.rememberMe').style.top = "-5px";
    document.querySelector('.btn_sign').innerHTML = "SIGN UP";
    setTimeout(function () {
        document.querySelector('.link_forgot_pass').className = "link_forgot_pass d_none";
        document.querySelector('.rememberMe').className = "rememberMe d_none";
    }, 450);

}


function sign_in() {
    "use strict"
    document.getElementById('loginForm').reset();
    document.getElementById('formType').value = 'signin';
    var inputs = document.querySelectorAll('.input_form_sign');
    document.querySelectorAll('.ul_tabs > li')[0].className = "active";
    document.querySelectorAll('.ul_tabs > li')[1].className = "";

    for (var i = 0; i < inputs.length; i++) {
        switch (i) {
            case 1:
                console.log(inputs[i].name);
                break;
            case 2:
                console.log(inputs[i].name);
            default:
                document.querySelectorAll('.input_form_sign')[i].className = "input_form_sign d_block";
        }
    }

    setTimeout(function () {
        for (var d = 0; d < inputs.length; d++) {
            switch (d) {
                case 1:
                    console.log(inputs[d].name);
                    break;
                case 2:
                    console.log(inputs[d].name);

                default:
                    document.querySelectorAll('.input_form_sign')[d].className = "input_form_sign d_block";
                    document.querySelectorAll('.input_form_sign')[2].className = "input_form_sign d_block active_inp";

            }
        }
    }, 100);


    setTimeout(function () {
        document.querySelector('.rememberMe').className = "rememberMe d_block";
        document.querySelector('.link_forgot_pass').className = "link_forgot_pass d_block";

    }, 500);

    setTimeout(function () {

        document.querySelector('.link_forgot_pass').style.opacity = "1";
        document.querySelector('.link_forgot_pass').style.top = "5px";
        document.querySelector('.rememberMe').style.opacity = "1";
        document.querySelector('.rememberMe').style.top = "5px";


        for (var d = 0; d < inputs.length; d++) {

            switch (d) {
                case 1:
                    console.log(inputs[d].name);
                    break;
                case 2:
                    console.log(inputs[d].name);

                    break;
                default:
                    document.querySelectorAll('.input_form_sign')[d].className = "input_form_sign";
            }
        }
    }, 1500);
    document.querySelector('.btn_sign').innerHTML = "SIGN IN";
}


window.onload = function () {
    "use strict";
    document.querySelector('.cont_centrar').className = "cont_centrar cent_active";

};

function postData(url = '', data = {}) {
    // Default options are marked with *
    return fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data) // body data type must match "Content-Type" header
    })
        .then(response => response.json()); // parses JSON response into native JavaScript objects
}

document.querySelectorAll('input').forEach(field => field.addEventListener('focus', () => {
    "use strict";
    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('successMessage').style.display = 'none';
}));
document.getElementById('loginForm').addEventListener('submit', (e) => {
    "use strict";
    e.preventDefault();
    const formD = document.getElementById('loginForm');
    const formO = new FormData(formD);
    const formOb = Object.fromEntries(formO);
    if (formOb.formType === 'signup') {
        console.log(formOb, formOb.password !== formOb.confirmPassword)
        if (formOb.password !== formOb.confirmPassword) {
            document.getElementById('errorMessage').textContent = 'Password!=ConfirmPassword';
            document.getElementById('errorMessage').style.display = 'block';
            return 0;
        }
        postData('https://vehispot.onrender.com/users/register/', formOb).then(data => {
            if (data.status) {
                document.getElementById('successMessage').textContent = data.message;
                document.getElementById('successMessage').style.display = "block";
                setTimeout(function () {
                    window.location.href = '/account/action/required/';
                }, 1500);
            } else {
                document.getElementById('errorMessage').textContent = data.message;
                document.getElementById('errorMessage').style.display = "block";
            }


        });

    } else {
        console.log(formOb);
        postData('https://vehispot.onrender.com/users/login/', formOb).then(data => {
            if (data.status) {
                document.getElementById('successMessage').textContent = data.message;
                document.getElementById('successMessage').style.display = "block";
                setTimeout(function () {
                    if (data.rememberMe) {
                        setCookie('token', data.token, 7);
                    } else {
                        setCookie('token', data.token, 0.5);
                    }
                    window.location.href = '/';
                });
            } else {
                document.getElementById('errorMessage').textContent = data.message;
                document.getElementById('errorMessage').style.display = "block";
            }


        });
    }


});


