<?php
require_once 'config_session.php';
require_once 'dbh.php';
require_once 'check_imput.php';

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $token = trim($_POST['token'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $pwd = trim($_POST['pwd'] ?? '');
    $cpwd = trim($_POST['cpwd'] ?? '');
    
    $errors = [];

    try {
        // Verify token is valid and not expired
        $query = "SELECT email FROM password_resets 
                 WHERE token = :token";
        $stmt = $pdo->prepare($query);
        $stmt->execute([':token' => $token]);
        $result = $stmt->fetch();

        if (!$result || $result['email'] !== $email) {
            $errors[] = "Invalid or expired reset link";
        }

        // Validate new password
        $errors = array_merge($errors, validatePassword($pwd, $cpwd));

        if (!empty($errors)) {
            $_SESSION["reset_errors"] = $errors;
            header("Location: ../pages/reset-password.php?token=" . $token);
            die();
        }

        // Begin transaction
        $pdo->beginTransaction();

        // Update password
        $hashedPwd = password_hash($pwd, PASSWORD_BCRYPT, ["cost" => 12]);
        $stmt = $pdo->prepare("UPDATE users SET password = :password WHERE email = :email");
        $stmt->execute([
            ':password' => $hashedPwd,
            ':email' => $email
        ]);

        // Mark reset token as used
        $stmt = $pdo->prepare("DELETE FROM password_resets WHERE email = :email");
        $stmt->execute([':email' => $email]);        

        $pdo->commit();

        // Set success message and redirect to login
        $_SESSION["login_success"] = "Password has been reset successfully. Please login with your new password.";
        header("Location: ../pages/login.php");
        die();

    } catch (PDOException $e) {
        if ($pdo->inTransaction()) {
            $pdo->rollBack();
        }
        header("Location: ../pages/errors_pages/500.php");
        die();
    }
} else {
    header("Location: ../index.php");
    die();
}
