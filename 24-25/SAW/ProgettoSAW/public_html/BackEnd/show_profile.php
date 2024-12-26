<?php
require_once 'config_session.php';
require_once '../../dbh.php';

if (!isset($_SESSION["user_id"])) {
    header("Location: ../index.php");
    die();
}

try {
    $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
    $stmt->execute([$_SESSION["user_id"]]);
    $user = $stmt->fetch();

    // Store user data in session
    $_SESSION["profile_data"] = [
        "firstname" => $user["firstname"],
        "lastname" => $user["lastname"],
        "username" => $user["username"],
        "email" => $user["email"]
    ];

    //for test uncoment echo and coment header
    //echo "Email: " . $user["email"] . "\n";
    //echo "First Name: " . $user["firstname"] . "\n";
    //echo "Last Name: " . $user["lastname"] . "\n";
    header("Location: ../pages/profile.php");
    
    
    die();
} catch (PDOException $e) {
    $_SESSION["error"] = "Failed to fetch profile data";
    header("Location: ../index.php");
    die();
}
