<?php
require_once 'config_session.php';

if (!isset($_SESSION['user_id'])) {
    header("Location: ../pages/login.php");
    exit();
}

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: ../pages/index.php");
    die();
}

require_once '../../dbh.php';
require_once 'check_imput.php';

// set to TRUE for testing
$test = FALSE;
if (!$test) {
    $firstname = trim($_POST['firstname'] ?? '');
    $lastname = trim($_POST['lastname'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $username = trim($_POST['username'] ?? '');
    $old_password = trim($_POST['old_password'] ?? '');
    $new_password = trim($_POST['new_password'] ?? '');
    $confirm_password = trim($_POST['confirm_password'] ?? '');
    $user_id = $_SESSION["user_id"];
} else {
    $firstname = trim($_POST['firstname'] ?? '');
    $lastname = trim($_POST['lastname'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $username = $firstname;
    $user_id = $_SESSION["user_id"];
}

// Validate basic fields
$errors = validateBasicFields($firstname, $lastname, $email, $username);

try {
    // Check existing user excluding current user
    $errors = array_merge($errors, checkExistingUser($pdo, $email, $username, $user_id));

    $stmt = $pdo->prepare("SELECT email FROM users WHERE id = :id");
    $stmt->bindParam(":id", $user_id);
    $stmt->execute();
    $current_email = $stmt->fetchColumn();

    if ($email !== $current_email && !$test) {
        require_once '../../check_email.php';

        if ($response === "invalid") {
            $errors[] = "Please provide a valid email address";
        }
    }

    // Password validation if attempting to change password
    if (!empty($new_password) || !empty($confirm_password) || !empty($old_password)) {
        // Verify old password
        $stmt = $pdo->prepare("SELECT password FROM users WHERE id = :id");
        $stmt->bindParam(":id", $user_id);
        $stmt->execute();
        $current_user = $stmt->fetch();

        if (!password_verify($old_password, $current_user['password'])) {
            $errors["wrong_password"] = "Current password is incorrect";
        }

        // Validate new password
        $errors = array_merge($errors, validatePassword($new_password, $confirm_password));
    }

    if (!empty($errors)) {
        $_SESSION["errors"] = $errors;
        $_SESSION["data"] = [
            "firstname" => $firstname,
            "lastname" => $lastname,
            "email" => $email,
            "username" => $username
        ];
        header("Location: ../pages/edit_profile.php");
        die();
    }

    // Update user
    if (!empty($new_password)) {
        $hashedPwd = password_hash($new_password, PASSWORD_BCRYPT, ["cost" => 12]);
        $stmt = $pdo->prepare("UPDATE users SET firstname = :firstname, lastname = :lastname, 
                             email = :email, username = :username, password = :password WHERE id = :id");
        $stmt->bindParam(":password", $hashedPwd);
    } else {
        $stmt = $pdo->prepare("UPDATE users SET firstname = :firstname, lastname = :lastname, 
                             email = :email, username = :username WHERE id = :id");
    }
    
    $stmt->bindParam(":firstname", $firstname);
    $stmt->bindParam(":lastname", $lastname);
    $stmt->bindParam(":email", $email);
    $stmt->bindParam(":username", $username);
    $stmt->bindParam(":id", $user_id);
    $stmt->execute();

    // Update session
    unset($_SESSION["errors"], $_SESSION["data"]);
    $_SESSION["user_username"] = $username;
    $_SESSION["success"] = "Profile updated successfully";
    
    header("Location: show_profile.php");
    die();

} catch (PDOException $e) {
    header("Location: ../pages/errors_pages/500.php");
    die();
}
