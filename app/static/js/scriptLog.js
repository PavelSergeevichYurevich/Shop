const logForm = document.querySelector('#logForm')

logForm.addEventListener('submit', function(e) {e.preventDefault()})

async function reg(){
    let expDate = new Date;
    expDate.setTime((new Date).getTime() + 604800000);
    document.cookie = email+"="+name+";expires="+expDate.toGMTString()+";path=/";

    fetch("/customer/rec/", {
        method: "POST",
        headers: { "Accept": "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ 
            email: email,
            password: password,
            name: name
        })
    })
    .then(res => {
        if (res.redirected) {
            alert('Пользователь зарегистрирован')
            window.location.href = res.url;
            return;
        } 
        else
            return res.text();
        });
    
}

function check() {
    let cook = document.cookie;
    let str = cook.split('; ');
    let cookieObject = {};
    let curr;
    for (let i = 0; i < str.length; ++i) {
        curr = str[i].split('=');
        cookieObject[curr[0]] = curr[1];
    }
    let checkMail = document.querySelector("#email").value
    if (checkMail in cookieObject) {
        name = cookieObject[checkMail]
        url_redirect = '/tasks/'+name
        window.location.href=url_redirect
    }
}

async function log(){
    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;
    fetch("/check/", {
        method: "POST",
        headers: { "Accept": "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ 
            email: email,
            password: password
        })
    })
    .then(res => {
        if (res.redirected) {
            window.location.href = res.url;
            return;
        } 
        else
            return res.text();
        })
        .then(data => {
            document.getElementById("response").innerHTML = data;
        })
         .catch(error => {
            console.error(error);
        });
}