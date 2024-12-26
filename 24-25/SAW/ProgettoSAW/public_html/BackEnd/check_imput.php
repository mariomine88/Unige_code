<?php

function validateBasicFields($firstname, $lastname, $email, $username) {
    $errors = [];

    if (empty($firstname) || empty($lastname) || empty($email) || empty($username)) {
        $errors["empty_input"] = "All fields are required!";
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors["invalid_email"] = "Invalid email format!";
    }

    if (!preg_match("/^[a-zA-Z0-9_\.]+$/", $username)) {
        $errors["invalid_username"] = "Username can only contain letters and numbers!";
    }

    return $errors;
}

function validatePassword($password, $confirm_password) {
    $errors = [];

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
