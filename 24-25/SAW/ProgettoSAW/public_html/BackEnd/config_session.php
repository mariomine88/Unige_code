<?php

ini_set('session.use_only_cookies', 1);
ini_set('session.use_strict_mode', 1);

session_set_cookie_params([
    'lifetime' => 1800,
    'domain' => 'saw.dibris.unige.it',
    'path' => '/~s5577783/',
    'secure' => true,
    'httponly' => true
]);

session_start();
session_regenerate_id();

if (!isset($_SESSION['last_regenerate'])) {
    $_SESSION['last_regenerate'] = time();
}

if ($_SESSION['last_regenerate'] < time() - 1800) {
    session_regenerate_id();
    $_SESSION['last_regenerate'] = time();
}
// Check for remember me cookie
if (!isset($_SESSION['user_id']) && isset($_COOKIE['remember_me'])) {
    list($selector, $token) = explode(':', urldecode($_COOKIE['remember_me']));
    
    try {
        require_once '../../dbh.php';
        
        $query = "SELECT auth_tokens.*, users.username users.is_admin FROM auth_tokens 
                  JOIN users ON auth_tokens.user_id = users.id 
                  WHERE auth_tokens.selector = :selector AND auth_tokens.expires > NOW()";
        $stmt = $pdo->prepare($query);
        $stmt->execute([':selector' => $selector]);
        
        //if result is found
        if ($auth = $stmt->fetch(PDO::FETCH_ASSOC)) {
            if (password_verify($token, $auth['token'])) {
                $_SESSION['user_id'] = $auth['user_id'];
                $_SESSION['user_username'] = $auth['username'];
                $_SESSION['is_admin'] = $auth['is_admin'];
            }
        }
    } catch (PDOException $e) {
        header("Location: ../pages/errors_pages/500.php");
        die();
    }
}