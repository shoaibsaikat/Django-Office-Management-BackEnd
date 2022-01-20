# Django-Office-Management-BackEnd
Office Management System using Django Backend with REST

1. pip install django mysqlclient
2. pip install django-cors-headers


To generate requirement.txt file -> conda list -e > requirements.txt

# Sign-in Javascript code
var data = new FormData();
data.append("username", "shoaib.rahman");
data.append("password", "shoaibrahman");

var xhr = new XMLHttpRequest();
xhr.withCredentials = true;

xhr.addEventListener("readystatechange", function() {
  if(this.readyState === 4) {
    console.log(this.responseText);
  }
});

xhr.open("POST", "http://127.0.0.1:8000/user/signin/");
xhr.setRequestHeader("Cookie", "csrftoken=OZEoJMtoLCH2OS2Hfcm8uJGNR1uacPhXKuognvQgjjR4ATV3G7P8F3swxw5SvORN; sessionid=ddzgfxjpe42hs469nnusymej5ppxy7kf");

xhr.send(data);


# Sign-out Javascript code
var xhr = new XMLHttpRequest();
xhr.withCredentials = true;

xhr.addEventListener("readystatechange", function() {
  if(this.readyState === 4) {
    console.log(this.responseText);
  }
});

xhr.open("GET", "http://127.0.0.1:8000/user/signout/");
xhr.setRequestHeader("Cookie", "csrftoken=OZEoJMtoLCH2OS2Hfcm8uJGNR1uacPhXKuognvQgjjR4ATV3G7P8F3swxw5SvORN");

xhr.send();
