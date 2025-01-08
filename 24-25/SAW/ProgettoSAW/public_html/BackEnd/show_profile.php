<?php
require_once 'config_session.php';

if (!isset($_SESSION["user_id"])) {
    header("Location: ../index.php");
    die();
}

require_once '../../dbh.php';

try {
    $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
    $stmt->execute([$_SESSION["user_id"]]);
    $user = $stmt->fetch();

    // Store user data in session
    $_SESSION["data"] = [
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
    header("Location: ../pages/errors_pages/500.php");
    die();
}
