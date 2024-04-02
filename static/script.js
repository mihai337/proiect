
// const ip = "http://192.168.1.63:8000";
const ip = 'http://127.0.0.1:8000';


function logout() {
    sessionStorage.setItem("username",null);
    sessionStorage.setItem("password",null);
    sessionStorage.setItem("balance",null);            
    window.location.replace("/login");
}

function checkBalance(){

    var u = sessionStorage.getItem("username");

    fetch(ip+'/get-balance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: u }),
    })
        .then(response => response.json())
        .then(data => {
            // Handle the response from the server
            if(data.code == 200){
                sessionStorage.setItem("balance" , data.balance);
                document.getElementById("balanceAmount").textContent = "$" + data.balance;
            }
            else{
                alert("Balance check failed");
            }
            // console.log(data);
            // You can redirect or perform other actions based on the response
        })
        .catch(error => {
            alert("Error");
            console.error('Error:', error);
        });
}

function addFunds(){

    var u = sessionStorage.getItem("username");
    var a = document.getElementById("depositAmount").value;

    fetch(ip+'/addfunds', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: u , balance : a}),
    })
        .then(response => 
        {
            // Handle the response from the server
            if(response.status == 200){
                // sessionStorage.setItem("balance" , data.balance);
                alert("Deposit successfull");
            }
            else{
                alert("Deposit failed");
            }
            // console.log(data);
            // You can redirect or perform other actions based on the response
        })
        .catch(error => {
            alert("Error");
            console.error('Error:', error);
        });
}

function modifyBalance() {
    // const modifyAmount = parseFloat(document.getElementById('modifyAmount').value);
    // if (!isNaN(modifyAmount)) {
    //     currentUser.balance += modifyAmount;
    //     document.getElementById('balanceAmount').textContent = `$${currentUser.balance.toFixed(2)}`;
    // } else {
    //     alert('Please enter a valid number to modify the balance.');
    // }

    $.post('/trans' , {username : sessionStorage.getItem("username")},function(data){
        // $.currentUser.balance = data.balance;
        if(data.code == '200')
            alert(" ");
        document.getElementById("balanceAmount").textContent = "$" + data.modBalance;
    } , 'json')
}

function sendMoney(){
    var f = document.getElementById("friend").value;
    var a = document.getElementById("amount").value;
    var username = sessionStorage.getItem("username");
    alert(username);
    if(f == ''){
        alert("Do you even have friends?");
        return;
    }

    if(a == ''){
        alert("Do you even have money?");
        return;
    }

    fetch(ip+'/transfer?mainUser='+username, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: f, balance: a }),
    })
        .then(response => {
            if(response.status == 404){
                alert("Friend not found");
                return;
            }
            if(response.status == 200){
                alert("Transfer completed");
            }

            if(response.status == 401){
                alert("Hai sa nu furam bani");
            }

            if(response.status == 304){
                alert("Nu-ti permiti boss");
            }

        })
        .then(data => {
            // Handle the response from the server
           
            // showBalanceSection();
            // console.log(data);
            // You can redirect or perform other actions based on the response
        })
        .catch(error => {
            alert("Eroare");
            console.error('Error:', error);
        });

}

function sendBill() {
    var u = document.getElementById('sendTo').value;
    var a = document.getElementById('amount').value;
    var f = sessionStorage.getItem("username");

    if(u == '' || a == ''){
        alert("Completati toate campurile");
        return;
    }

    fetch(ip+'/sendbill', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ factName: f, username: u , amount : a }),
    })
        .then(response => {
            if(response.status == 200)
                alert("Bill sent");
            else{
                alert("Bill failed to send");
            }
        })
        
        .catch(error => {
            alert("Billing failed");
            console.error('Error:', error);
        });
}

function signin() { //adauga user type cu drop down menu
    var u = document.getElementById('new-username').value;
    var p = document.getElementById('new-password').value;
    var rp = document.getElementById('re-password').value;

    if (u == '' || p == '' || rp == '') {
        alert('Completaţi toate câmpurile');
        return;
    }

    if(p != rp){
        alert("Passwords don't match");
        return;
    }

    fetch(ip+'/sign-in', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: u, password: p }),
    })
        .then(response => {
            if(response.status == 200){
                alert("Sign in successfully, please log in");
                window.location.replace("/login");
            }
            else{
                alert("Sign in failed");
            }

        })
        .catch(error => {
            alert("Sign in failed");
            console.error('Error:', error);
        });
}

function doKeyPress(e) {
    if (window.event) { e = window.event; }
    if (e.keyCode == 13) {
        login();
    }
}

function login() {
    var u = document.getElementById('username').value;
    var p = document.getElementById('password').value;

    if(u == '' || p == ''){
        alert("Completati toate campurile");
        return;
    }

    fetch(ip+'/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: u, password: p }),
    })
        .then(response => response.json())
        .then(data => {
            // Handle the response from the server
            if(data.code == 200){
                sessionStorage.setItem("username", u);
                sessionStorage.setItem("password", p);
                sessionStorage.setItem("balance", data.balance);
                window.location.replace("/index/"+data.type);
            }
            else{
                alert("Login failed");
            }
            // showBalanceSection();
            // console.log(data);
            // You can redirect or perform other actions based on the response
        })
        .catch(error => {
            alert("Login failed");
            console.error('Error:', error);
        });
}

function payBill(name,uid){ //make the bill disappear
    fetch(ip+'/paybill/'+name+'/'+uid)
        .then(response => {
            if(response.status == 200){
                alert("Bill paid");    
            }
            else{
                alert("Bill failed to pay");
            }
        })
        
        .catch(error => {
            alert("Billing failed");
            console.error('Error:', error);
        });
}


function populateTaxes() {
    const taxesList = document.getElementById("taxesItems");
    taxesList.innerHTML = "";

    document.getElementById('loggedInUsername').textContent = sessionStorage.getItem("username");
        document.getElementById('balanceAmount').textContent = "$" + sessionStorage.getItem("balance");

        const taxesData = [
            { "name": "John Doe", "amount": 100 },
            { "name": "Jane Smith", "amount": 150 },
            { "name": "Mike Johnson", "amount": 80 },
            { "name": "Emily Brown", "amount": 120 },
            { "name": "David Wilson", "amount": 90 },
            { "name": "Sarah Miller", "amount": 110 },
            { "name": "Michael Davis", "amount": 95 },
            { "name": "Jennifer Garcia", "amount": 135 },
            { "name": "Robert Martinez", "amount": 70 },
            { "name": "Linda Hernandez", "amount": 125 },
   
        ];

    fetch(ip+"/getbills/" + sessionStorage.getItem("username"))
        .then(response => response.json())
        .then((data) =>{
            data.forEach(person => {
                const listItem = document.createElement("li");
                listItem.textContent = `${person.factName}: $${person.amount.toFixed(2)}`;
                const payButton = document.createElement("button");
                payButton.textContent = "Pay";
                payButton.onclick = function () {
                    payBill(person.username,person.uid);
                    console.log(person.username);
                };
    
                listItem.appendChild(payButton);
                taxesList.appendChild(listItem);
            });
        });
        // taxesData.forEach(person => {
        //     const listItem = document.createElement("li");
        //     listItem.textContent = `${person.name}: $${person.amount.toFixed(2)}`;
    
        //     const payButton = document.createElement("button");
        //     payButton.textContent = "Pay";
        //     payButton.onclick = function () {
        //         console.log(`Paying ${person.name}`);
        //         // Add payment logic or redirection here
        //     };
    
        //     listItem.appendChild(payButton);
        //     taxesList.appendChild(listItem);
        // });
}


function populateHistory() {
    const historyList = document.getElementById("historyItems");
    historyList.innerHTML = "";

    fetch(ip + "/gethistory/" + sessionStorage.getItem("username"))
        .then(response => response.json())
        .then((data) => {
            data.forEach(transaction => {
                if(transaction.to){
                    console.log(transaction);
                    const listItem = document.createElement("li");
                    listItem.textContent = `${transaction.from}->${transaction.to}: ${transaction.message} - $${transaction.amount}`;
                    historyList.appendChild(listItem);
                }
                else{
                    console.log(transaction);
                    const listItem = document.createElement("li");
                    listItem.textContent = `${transaction.from}: ${transaction.message} - $${transaction.amount}`;
                    historyList.appendChild(listItem);
                }
            });
        })
        .catch(error => {
            console.error('Error fetching transaction data:', error);
        });
}

function showSection() {
    const selectBox = document.getElementById("sectionSelect");
    const selectedValue = selectBox.options[selectBox.selectedIndex].value;

    const sections = ["balance", "transfer", "addFunds", "taxes","history"]; 

    sections.forEach(sectionId => {
        const sectionElement = document.getElementById(sectionId + "Content"); // Updated ID to match HTML
        if (sectionElement) {
            if (sectionId === selectedValue) {
                sectionElement.style.display = "block";
            } else {
                sectionElement.style.display = "none";
            }
        } else {
            console.error("Element not found:", sectionId + "Content");
        }
    });

    if (selectedValue === "taxes") {
        populateTaxes();
        document.getElementById("taxesContent").style.display = "block"; 
        document.getElementById("balanceSection").style.display="none";
    }
    else if(selectedValue =="history"){
        populateHistory();
        document.getElementById("historyContent").style.display = "block"; 
        document.getElementById("balanceSection").style.display="none";
    }
    else {
        document.getElementById("balanceSection").style.display = "block";
    }
    
}