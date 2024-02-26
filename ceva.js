function dologin() {
    var u = document.getElementById('username').value;
    var p = document.getElementById('password').value;
    if (u == '' || p == '') {
        alert('Completaţi toate câmpurile');
        return;
    }

    $.post('/login', { username: u, password: p }, function (data) {
        if (data.code == '200') {
            currentUser = { username: u, balance: data.balance }
            showBalanceSection();
        }
        else{
            alert("Login failed");
        }
    }, 'json');
}