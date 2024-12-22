<?php
require_once 'config_session.php';

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $usernameOrEmail = trim($_POST["username"] ?? '');
    $pwd = trim($_POST["pwd"] ?? '');

    $errors = [];

    // Validate empty fields
    if (empty($usernameOrEmail) || empty($pwd)) {
        $errors["empty_input"] = "All fields are required!";
    }

    try {
        require_once 'dbh.php';

        if (empty($errors)) {
            // Check if input is email or username
            $query = "SELECT * FROM users WHERE username = :identifier OR email = :identifier;";
            $stmt = $pdo->prepare($query);
            $stmt->bindParam(":identifier", $usernameOrEmail);
            $stmt->execute();

            $user = $stmt->fetch(PDO::FETCH_ASSOC);

            $pdo = null;
            $stmt = null;
            
            if (!$user) {
                $errors["login_incorrect"] = "Invalid credentials!";
            } else {
                // Verify password
                if (!password_verify($pwd, $user["password"])) {
                    $errors["login_incorrect"] = "Invalid credentials!";
                }
            }
        }

        if (!empty($errors)) {
            $_SESSION["login_errors"] = $errors;
            $_SESSION["login_data"] = [
                "username" => $usernameOrEmail
            ];
            header("Location: ../pages/login.php");
            die();
        }

        session_regenerate_id(); // Regenerate session ID and delete the old one

        // If no errors, log the user in
        $_SESSION["user_id"] = $user["id"];
        $_SESSION["user_username"] = $user["username"];
        

        // Clear any existing errors
        unset($_SESSION["login_errors"]);
        unset($_SESSION["login_data"]);

        // Redirect to dashboard or home page
        header("Location: ../index.php");
        die();

    } catch (PDOException $e) {
        header("Location: ../pages/errors_pages/500.php");
        die();
    }
} else {
    header("Location: ../index.php");
    die();
}
