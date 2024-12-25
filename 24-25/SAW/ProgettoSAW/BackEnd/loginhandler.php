<?php
require_once 'config_session.php';

function setRememberMeCookie($userId, $pdo) {
    $selector = bin2hex(random_bytes(16));
    $token = random_bytes(32);
    $hashedToken = password_hash($token, PASSWORD_BCRYPT);
    $expiry = date('Y-m-d H:i:s', time() + 30 * 24 * 60 * 60); // 30 days

    // Clear existing tokens and save new one
    $pdo->prepare("DELETE FROM auth_tokens WHERE user_id = :user_id")
        ->execute([':user_id' => $userId]);
    
    $pdo->prepare("INSERT INTO auth_tokens (user_id, selector, token, expires) 
                   VALUES (:user_id, :selector, :token, :expires)")
        ->execute([
            ':user_id' => $userId,
            ':selector' => $selector,
            ':token' => $hashedToken,
            ':expires' => $expiry
        ]);

    setcookie(
        'remember_me',
        $selector . ':' . bin2hex($token),
        time() + 30 * 24 * 60 * 60
    );
}

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: ../index.php");
    die();
}

try {
    $usernameOrEmail = trim($_POST["username"] ?? '');
    $pwd = trim($_POST["pwd"] ?? '');
    
    if (empty($usernameOrEmail) || empty($pwd)) {
        $_SESSION["login_errors"]["empty_input"] = "All fields are required!";
        header("Location: ../pages/login.php");
        die();
    }

    require_once 'dbh.php';
    
    // Check credentials
    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = :identifier OR email = :identifier");
    $stmt->execute([':identifier' => $usernameOrEmail]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$user || !password_verify($pwd, $user["password"])) {
        $_SESSION["login_errors"]["login_incorrect"] = "Invalid credentials!";
        $_SESSION["login_data"]["username"] = $usernameOrEmail;
        header("Location: ../pages/login.php");
        die();
    }

    // Login successful
    session_regenerate_id();
    $_SESSION["user_id"] = $user["id"];
    $_SESSION["user_username"] = $user["username"];

    // Handle remember me
    if (isset($_POST["remember"])) {
        setRememberMeCookie($user["id"], $pdo);
    }

    // Clear session data and redirect
    unset($_SESSION["login_errors"], $_SESSION["login_data"]);
    header("Location: ../index.php");
    die();

} catch (PDOException $e) {
    header("Location: ../pages/errors_pages/500.php");
    die();
}
