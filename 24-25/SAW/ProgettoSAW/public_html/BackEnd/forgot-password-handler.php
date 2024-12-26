<?php
require_once 'config_session.php';
require_once '../../dbh.php';
require_once '../../mail-init.php';

// Redirect if not POST
if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: ../pages/forgot-password.php");
    die();
}

// Get and validate email
$email = trim($_POST['email'] ?? '');
$errors = [];

if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $_SESSION["reset_data"] = ["email" => $email];
    $_SESSION["reset_errors"] = ["Invalid email address"];
    header("Location: ../pages/forgot-password.php");
    die();
}

try {
    // Check if email exists
    $stmt = $pdo->prepare("SELECT email FROM users WHERE email = :email");
    $stmt->execute([':email' => $email]);
    
    $_SESSION["reset_data"] = ["email" => $email];
    $_SESSION["reset_errors"] = ["If this email exists, you will receive reset instructions"];
    
    if (!$stmt->fetch()) {
        header("Location: ../pages/forgot-password.php");
        die();
    }

    // Generate token and handle database operations in transaction
    $token = urlencode(bin2hex(random_bytes(32)));
    $expires = date('Y-m-d H:i:s', strtotime('+1 hour'));

    $pdo->beginTransaction();
    
    // Remove old tokens
    $stmt = $pdo->prepare("DELETE FROM password_resets WHERE email = :email");
    $stmt->execute([':email' => $email]);

    // Insert new token
    $stmt = $pdo->prepare("INSERT INTO password_resets (email, token, expires_at) VALUES (:email, :token, :expires_at)");
    $stmt->execute([
        ':email' => $email,
        ':token' => $token,
        ':expires_at' => $expires
    ]);
    
    $pdo->commit();

    // Send email
    $resetLink = "https://saw.dibris.unige.it/~s5577783/pages/reset-password.php?token=" . $token;
    
    try {
        $mail->setFrom('saws5577783donotreply@gmail.com', 'Password Reset');
        $mail->addAddress($email);
        $mail->isHTML(true);
        $mail->Subject = 'Password Reset Request';
        $mail->Body = "
            <h2>Password Reset Request</h2>
            <p>You have requested to reset your password.</p>
            <p>Please click the link below to reset your password:</p>
            <p><a href='{$resetLink}'>Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
        ";
        $mail->AltBody = "Reset your password: {$resetLink}";
        $mail->send();
        
    } catch (Exception $e) { }

    header("Location: ../pages/forgot-password.php");
    die();

} catch (PDOException $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    header("Location: ../pages/errors_pages/500.php");
    die();
}