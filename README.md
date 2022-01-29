# Django-Office-Management-BackEnd
Office Management System using Django Backend with REST api support.
It can be consumed by different front-ends like Angular, React or Vue.js.

Some requirements:
1. pip install django mysqlclient
2. pip install django-cors-headers

Note: To generate requirement.txt file -> conda list -e > requirements.txt





# Sign-in Test from Browser
<html>

<body>
  <form action="http://127.0.0.1:8000/user/signin/" method="POST">
    <div>
      <label for="username">Username</label>
      <input type="text" name="username" id="username" value="shoaib.rahman">
    </div>
    <div>
      <label for="password">Password</label>
      <input type="password" name="password" id="password" value="shoaibrahman">
    </div>
    <div>
      <button>Login</button>
    </div>
  </form>
</body>
</html>