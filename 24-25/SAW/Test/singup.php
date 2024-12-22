<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>

    <H3>sign up</H3>

    <form action="include/singuphandlere.php" method="post">
        <input type="text" name="firstname" placeholder="firstname">
        <input type="text" name="lastname" placeholder="lastname">
        <br>
        <input type="text" name="email" placeholder="Email">
        <br>
        <input type="text" name="username" placeholder="Username">
        <br>
        <input type="password" name="password" placeholder="Password">
        <input type="password" name="cpassword" placeholder="Confirm Password">
        <br>
        <button type="submit" name="submit">Singup</button>
    </form>
    
</body>
</html>