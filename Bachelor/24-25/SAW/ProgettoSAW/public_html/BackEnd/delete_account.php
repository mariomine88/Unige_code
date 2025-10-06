<?php
require_once 'config_session.php';

if (!isset($_SESSION["user_id"])) {
    header("Location: ../index.php");
    die();
}

try {
    require_once '../../dbh.php';
    $user_id = $_SESSION["user_id"];
    
    $query = "DELETE FROM users WHERE id = :user_id;";
    $stmt = $pdo->prepare($query);
    $stmt->bindParam(":user_id", $user_id);
    $stmt->execute();
    
    // Clear session and redirect
    session_unset();
    session_destroy();
    
    header("Location: ../pages/index.php?deletion=success");
    die();
} catch (PDOException $e) {
    header("Location: ../pages/errors_pages/500.php");
    die();
}
