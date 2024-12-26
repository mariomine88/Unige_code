<?php

function validateBasicFields($firstname, $lastname, $email, $username) {
    $errors = [];

    // Empty validation checks
    if (empty($firstname) || empty($lastname) || empty($email) || empty($username)) {
        $errors["empty_input"] = "All fields are required!";
    }

    // Email validation checks
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors["invalid_email"] = "Invalid email format!";
    }

    // Username validation checks
    if (!preg_match("/^[a-zA-Z0-9_\.]+$/", $username)) {
        $errors["invalid_username"] = "Username can only contain letters and numbers!";
    }

    // Length validation checks
    if (strlen($firstname) > 50) {
        $errors["firstname_length"] = "First name must be less than 50 characters";
    }
    if (strlen($lastname) > 50) {
        $errors["lastname_length"] = "Last name must be less than 50 characters";
    }
    if (strlen($email) > 100) {
        $errors["email_length"] = "Email must be less than 100 characters";
    }
    if (strlen($username) > 50) {
        $errors["username_length"] = "Username must be less than 50 characters";
    }

    return $errors;
}

function validatePassword($password, $confirm_password) {
    $errors = [];

    //min 8 characters, at least one uppercase letter, one lowercase letter and one number
    if (strlen($password) < 8) {
        $errors["weak_password"] = "Password must be at least 8 characters long!";
    }
    if (!preg_match("/[A-Z]/", $password)) {
        $errors["weak_password"] = "Password must contain at least one uppercase letter!";
    }
    if (!preg_match("/[a-z]/", $password)) {
        $errors["weak_password"] = "Password must contain at least one lowercase letter!";
    }
    if (!preg_match("/[0-9]/", $password)) {
        $errors["weak_password"] = "Password must contain at least one number!";
    }

    // Password match validation
    if ($password !== $confirm_password) {
        $errors["password_match"] = "Passwords do not match!";
    }

    return $errors;
}

function checkExistingUser($pdo, $email, $username, $exclude_id = null) {
    $errors = [];
    
    // Check username
    $query = "SELECT username FROM users WHERE username = :username";
    $params = [":username" => $username];
    
    if ($exclude_id !== null) {
        $query .= " AND id != :id";
        $params[":id"] = $exclude_id;
    }
    
    $stmt = $pdo->prepare($query);
    foreach ($params as $key => &$val) {
        $stmt->bindParam($key, $val);
    }
    $stmt->execute();
    
    if ($stmt->rowCount() > 0) {
        $errors["username_taken"] = "Username already exists!";
    }

    // Check email
    $query = "SELECT email FROM users WHERE email = :email";
    $params = [":email" => $email];
    
    if ($exclude_id !== null) {
        $query .= " AND id != :id";
        $params[":id"] = $exclude_id;
    }
    
    $stmt = $pdo->prepare($query);
    foreach ($params as $key => &$val) {
        $stmt->bindParam($key, $val);
    }
    $stmt->execute();
    
    if ($stmt->rowCount() > 0) {
        $errors["email_taken"] = "Email already registered!";
    }

    return $errors;
}
