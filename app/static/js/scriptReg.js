const regForm = document.querySelector('#regForm')

regForm.addEventListener('submit', function(e) {e.preventDefault()})

async function reg(){
    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;
    const name = document.querySelector("#name").value;     
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
