<?php
require_once 'config_session.php';
require_once '../../dbh.php';
require_once 'check_imput.php';

if ($_SERVER["REQUEST_METHOD"] === "POST") {
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
        $username = "test";
        $user_id = $_SESSION["user_id"];
    }


    // Validate basic fields
    $errors = validateBasicFields($firstname, $lastname, $email, $username);

    try {
        // Check existing user excluding current user
        $errors = array_merge($errors, checkExistingUser($pdo, $email, $username, $user_id));

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
            $_SESSION["update_errors"] = $errors;
            $_SESSION["update_data"] = [
                "firstname" => $firstname,
                "lastname" => $lastname,
                "email" => $email,
                "username" => $username
            ];
            header("Location: ../pages/profile.php");
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
        unset($_SESSION["update_errors"], $_SESSION["update_data"]);
        $_SESSION["user_username"] = $username;
        $_SESSION["profile_updated"] = true;
        
        header("Location: show_profile.php");
        die();

    } catch (PDOException $e) {
        $_SESSION["error"] = "Update failed: Database error";
        header("Location: ../pages/profile.php");
        die();
    }
} else {
    header("Location: ../index.php");
    die();
}
