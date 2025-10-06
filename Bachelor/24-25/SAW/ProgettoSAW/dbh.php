<?php

$config = json_decode(file_get_contents(__DIR__ . '/config.json'), true);
$db = $config['database'];

$host = $db['host'];
$dbname = $db['name'];
$dns = 'mysql:host=' . $host . ';dbname=' . $dbname;
$dbusername = $db['username'];
$dbpassword = $db['password'];

try {
    $pdo = new PDO($dns, $dbusername, $dbpassword);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    header("Location: ../pages/errors_pages/500.php");
    die();
}

