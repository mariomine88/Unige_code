<?php

ini_set('session.use_only_cookies', 1);
ini_set('session.use_strict_mode', 1);

session_set_cookie_params([
    'lifetime' => 1800,
    'domain' => 'localhost',
    'path' => '/',
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