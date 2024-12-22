<?php
require_once 'config_session.php';

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $firstname = trim($_POST['firstname'] ?? '');
    $lastname = trim($_POST['lastname'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $username = trim($_POST['username'] ?? '');
    $pwd = trim($_POST['pwd'] ?? '');
    $cpwd = trim($_POST['cpwd'] ?? '');

    $errors = [];

    // Validate empty fields
    if (empty($firstname) || empty($lastname) || empty($email) || empty($username) || empty($pwd) || empty($cpwd)) {
        $errors["empty_input"] = "All fields are required!";
    }

    // Validate email
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors["invalid_email"] = "Invalid email format!";
    }

    // Validate password strength
    if (strlen($pwd) < 8) {
        $errors["weak_password"] = "Password must be at least 8 characters long!";
    }
    if (!preg_match("/[A-Z]/", $pwd)) {
        $errors["weak_password"] = "Password must contain at least one uppercase letter!";
    }
    if (!preg_match("/[a-z]/", $pwd)) {
        $errors["weak_password"] = "Password must contain at least one lowercase letter!";
    }
    if (!preg_match("/[0-9]/", $pwd)) {
        $errors["weak_password"] = "Password must contain at least one number!";
    }

    // Check if passwords match
    if ($pwd !== $cpwd) {
        $errors["password_match"] = "Passwords do not match!";
    }

    try {
        require_once 'dbh.php';
        
        // Check if username exists
        $stmt = $pdo->prepare("SELECT username FROM users WHERE username = :username");
        $stmt->bindParam(":username", $username);
        $stmt->execute();
        if ($stmt->rowCount() > 0) {
            $errors["username_taken"] = "Username already exists!";
        }

        // Check if email exists
        $stmt = $pdo->prepare("SELECT email FROM users WHERE email = :email");
        $stmt->bindParam(":email", $email);
        $stmt->execute();
        if ($stmt->rowCount() > 0) {
            $errors["email_taken"] = "Email already registered!";
        }

        // If there are errors, store them in session and redirect
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

        // If no errors, proceed with insertion
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

        // Clear any existing errors and set success message
        unset($_SESSION["signup_errors"]);
        unset($_SESSION["signup_data"]);
        $_SESSION["signup_success"] = "Account created successfully! Please login.";

        header("Location: ../pages/login.php");
        die();

    } catch (PDOException $e) {
        header("Location: ../pages/errors_pages/500.php");
        die();
    }
} else {
    header("Location: ../index.php");
    die();
}