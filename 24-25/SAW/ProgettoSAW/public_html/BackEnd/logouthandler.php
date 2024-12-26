<?php
require_once 'config_session.php';

try {
    if (isset($_SESSION["user_id"])) {
        require_once '../dbh.php';
        
        // Delete auth tokens from database
        $stmt = $pdo->prepare("DELETE FROM auth_tokens WHERE user_id = :user_id");
        $stmt->execute([':user_id' => $_SESSION["user_id"]]);

        // Delete remember me cookie with all parameters
        setcookie("remember_me", "", time() - 60 *60);
        
        // Clear session
        session_unset();
        session_destroy();
    }
    
    header("Location: ../index.php");
    die();
    
} catch (PDOException $e) {
    header("Location: ../pages/errors_pages/500.php");
    die();
}
