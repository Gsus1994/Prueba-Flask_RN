document.getElementById('login-btn').addEventListener('click', function() {
    login();
});

document.getElementById('password').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        login();
    }
});

function login() {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    
    fetch(loginUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username, password: password })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';

        if (data.access_token) {
            localStorage.setItem('token', data.access_token);
            window.location.href = mapUrl;                
        } else {
            alert('Login fallido');
        }
    })
    .catch(error => {
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
        console.error('Error en la solicitud:', error);
    });
}