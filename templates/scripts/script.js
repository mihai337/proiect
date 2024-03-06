// let currentUser = null;

// function checkBalance(){
//     var u = document.getElementById('username').value;

//     fetch('http://192.168.1.10:8000/get-balance', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ name: u }),
//     })
//         .then(response => response.json())
//         .then(data => {
//             // Handle the response from the server
//             if(data.code == 200){
//                 currentUser.balance = data.balance;
//                 document.getElementById("balanceAmount").textContent = "$" + data.balance+".00";
//             }
//             else{
//                 alert("Balance check failed ${currentUser.username}");
//             }
//             // console.log(data);
//             // You can redirect or perform other actions based on the response
//         })
//         .catch(error => {
//             alert("Login failed");
//             console.error('Error:', error);
//         });
// }

// function login() { //asta merge
//     var u = document.getElementById('username').value;
//     var p = document.getElementById('password').value;

//     if(u == '' || p == ''){
//         alert("Completati toate campurile");
//         return;
//     }

//     fetch('http://192.168.1.10:8000/login', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ name: u, password: p }),
//     })
//         .then(response => response.json())
//         .then(data => {
//             // Handle the response from the server
//             if(data.code == 200){
//                 currentUser = { username: u, password : p, balance: data.balance };
//                 window.location.replace("/index");
//             }
//             else{
//                 alert("Login failed");
//             }
//             // showBalanceSection();
//             // console.log(data);
//             // You can redirect or perform other actions based on the response
//         })
//         .catch(error => {
//             alert("Login failed");
//             console.error('Error:', error);
//         });
// }

// function modifyBalance() {
//     // const modifyAmount = parseFloat(document.getElementById('modifyAmount').value);
//     // if (!isNaN(modifyAmount)) {
//     //     currentUser.balance += modifyAmount;
//     //     document.getElementById('balanceAmount').textContent = `$${currentUser.balance.toFixed(2)}`;
//     // } else {
//     //     alert('Please enter a valid number to modify the balance.');
//     // }

//     $.post('/trans' , {username : currentUser.username},function(data){
//         // $.currentUser.balance = data.balance;
//         if(data.code == '200')
//             alert(" ");
//         document.getElementById("balanceAmount").textContent = "$" + data.modBalance+".00";
//     } , 'json')
// }

// function modifyBalance() {
//     // const modifyAmount = parseFloat(document.getElementById('modifyAmount').value);
//     // if (!isNaN(modifyAmount)) {
//     //     currentUser.balance += modifyAmount;
//     //     document.getElementById('balanceAmount').textContent = `$${currentUser.balance.toFixed(2)}`;
//     // } else {
//     //     alert('Please enter a valid number to modify the balance.');
//     // }

//     $.post('/trans' , {username : currentUser.username},function(data){
//         // $.currentUser.balance = data.balance;
//         if(data.code == '200')
//             alert(" ");
//         document.getElementById("balanceAmount").textContent = "$" + data.modBalance+".00";
//     } , 'json')
// }

// function showLogin() {
//     document.getElementById('signin-div').style.display = 'none';
//     document.getElementById('login-div').style.display = 'block';
// }

// function showBalanceSection() {
//     document.getElementById('loggedInUsername').textContent = currentUser.username;
//     document.getElementById('balanceAmount').textContent = `$${currentUser.balance.toFixed(2)}`;
//     document.getElementById("username").textContent = '';
//     document.getElementById("password").textContent='';
//     document.getElementById('login-div').style.display = 'none';
//     document.getElementById('balanceSection').style.display = 'block';
// }

// function logout() {
//     currentUser = null;
//     document.getElementById('balanceSection').style.display = 'none';
//     document.getElementById('login-div').style.display = 'block';
//     document.getElementById('username').textContent = '';
//     document.getElementById("password").textContent='';

// }