function init() {
}

var loginOk=false;

function validateFirstName() {
    var firstname = document.getElementById("firstnameForm").value;
    if (firstname === "") {
        document.getElementById("firstnameErr").innerHTML = "Pole obowiązkowe.";
        return false;
    }
    else {
        if (/[^a-zA-Z]/.test(firstname)) {
            document.getElementById("firstnameErr").innerHTML = "Imię może zawierać tylko litery.";
            return false;
        }
        else {
            document.getElementById("firstnameErr").innerHTML = "";
            return true;
        }
    }
}

function validateLastName() {
    var lastname = document.getElementById("lastnameForm").value;
    if (lastname === "") {
        document.getElementById("lastnameErr").innerHTML = "Pole obowiązkowe.";
        return false;
    }
    else {
        if (/[^a-zA-Z]/.test(lastname)) {
            document.getElementById("lastnameErr").innerHTML = "Nazwisko może zawierać tylko litery.";
            return false;
        }
        else {
            document.getElementById("lastnameErr").innerHTML = "";
            return true;
        }
    }
}


function validatePesel() {
    var pesel = document.getElementById("peselForm").value;
    if (pesel === "") {
        document.getElementById("peselErr").innerHTML = "Pole obowiązkowe.";
        return false;
    }
    else {
        if (/^[0-9]*$/.test(pesel)) {
            if (pesel.length != 11) {
                document.getElementById("peselErr").innerHTML = "PESEL musi mieć 11 cyfr.";
                return false;
            }
            else {
                document.getElementById("peselErr").innerHTML = "";
            }
        }
        else {
            document.getElementById("peselErr").innerHTML = "PESEL może zawierać tylko cyfry.";
            return false;
        }
    }
    if ((pesel[9] % 2) == 1) {
        document.getElementById("sexm").checked = true;
    } else {
        document.getElementById("sexf").checked = true;
    }
    return true;
}

function validateDate() {
    if (document.getElementById("datebirthForm").value === "") {
        document.getElementById("datebirthErr").innerHTML = "Pole obowiazkowe.";
        return false;
    }
    else {
        document.getElementById("datebirthErr").innerHTML = "";
        return true;
    }
}

function validatePhoto() {
    if (document.getElementById("photoForm").value === "") {
        document.getElementById("photoErr").innerHTML = "Nie wybrano zdjecia.";
        return false;
    }
    else {
        document.getElementById("photoErr").innerHTML = "";
        return true;
    }
}

function validateLogin() {
    var login = document.getElementById("loginForm").value;
    var url = "http://edi.iem.pw.edu.pl/chaberb/register/check/" + login;
    if (login == "") {
        document.getElementById("loginErr").innerHTML = "Pole obowiązkowe.";
        return false;
    }
    else {
        fetch(url)
            .then(response => response.text())
            .then(data => {
                if (data.includes("true")) {
                    document.getElementById("loginErr").innerHTML = "Login zajęty.";
                    document.getElementById("loginErr").style = "color: red;";
                    loginOk=false;
                }
                else {
                    document.getElementById("loginErr").innerHTML = "Login ok.";
                    document.getElementById("loginErr").style = "color: green;";
                    loginOk=true;
                }
            })
            .catch(function (error) {
                console.log(error);
            });
    }
}

function validatePassword() {
    var password = document.getElementById("passwordForm").value;
    if (password === "") {
        document.getElementById("passwordErr").innerHTML = "Pole obowiązkowe.";
        return false;
    }
    else {
        if (password.length < 8) {
            document.getElementById("passwordErr").innerHTML = "Hasło musi mieć conajmniej 8 znaków.";
            return false;
        }
        else {
            if (!(/[\d]/.test(password))) {
                document.getElementById("passwordErr").innerHTML = "Hasło musi zawierać cyfry.";
                return false;
            }
            else {
                if (!(/[\W]/.test(password))) {
                    document.getElementById("passwordErr").innerHTML = "Hasło musi zawierać znaki specjalne.";
                    return false;
                }
                else {
                    document.getElementById("passwordErr").innerHTML = "";
                    return true;
                }
            }
        }
    }
}

function validateRepassword() {
    var password = document.getElementById("passwordForm").value;
    var repassword = document.getElementById("repasswordForm").value;
    document.getElementById("repasswordErr").innerHTML = " ";

    if (repassword.localeCompare(password) || repassword === "") {
        document.getElementById("repasswordErr").innerHTML = "Hasła nie są jednakowe!";
        return false;
    }
    else {
        return true;
    }
}


function val() {
    console.log("wciśnięty");
    validateLogin();
    var isOk = true;
    isOk = validateFirstName();
    isOk = validateLastName();
    isOk = validateDate();
    isOk = validatePesel();
    isOk = validatePhoto();
    isOk = validatePassword();
    isOk = validateRepassword();
    if(isOk && loginOk)
    {
        document.getElementById("formRegister").submit();
    }
}