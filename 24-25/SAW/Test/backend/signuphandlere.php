<?php
require_once 'config_session.php';
require_once 'dbh.php';
require_once 'check_imput.php';

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $firstname = trim($_POST['firstname'] ?? '');
    $lastname = trim($_POST['lastname'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $username = trim($_POST['username'] ?? '');
    $pwd = trim($_POST['pwd'] ?? '');
    $cpwd = trim($_POST['cpwd'] ?? '');

    // Validate basic fields
    $errors = validateBasicFields($firstname, $lastname, $email, $username);
    
    // Validate password
    $errors = array_merge($errors, validatePassword($pwd, $cpwd));

    try {
        // Check for existing user
        $errors = array_merge($errors, checkExistingUser($pdo, $email, $username));

        if (!empty($errors)) {
            $_SESSION["signup_errors"] = $errors;
            $_SESSION["signup_data"] = [
                "firstname" => $firstname,
                "lastname" => $lastname,
                "email" => $email,
                "username" => $username
            ];
            header("Location: ../pages/signup.php");
            die();
        }

        // Insert new user
        $hashedPwd = password_hash($pwd, PASSWORD_BCRYPT, ["cost" => 12]);
        
        $query = "INSERT INTO users (firstname, lastname, email, username, password) 
                 VALUES (:firstname, :lastname, :email, :username, :password)";
        $stmt = $pdo->prepare($query);
        
        $stmt->bindParam(":firstname", $firstname);
        $stmt->bindParam(":lastname", $lastname);
        $stmt->bindParam(":email", $email);
        $stmt->bindParam(":username", $username);
        $stmt->bindParam(":password", $hashedPwd);
        
        $stmt->execute();

        // Clear session and set success
        unset($_SESSION["signup_errors"], $_SESSION["signup_data"]);
        $_SESSION["signup_success"] = "Account created successfully! Please login.";
        
        header("Location: ../pages/signup.php");
        die();

    } catch (PDOException $e) {
        header("Location: ../pages/errors_pages/500.php");
        die();
    }
}