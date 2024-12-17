<?php


$dns = 'mysql:host=localhost;dbname=sawdb';    // Data Source
$dbusername = "root";    // Database Username
$dbpassword = "";    // Database Password

try {
    $pdo = new PDO($dns, $dbusername, $dbpassword);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    echo "Connected Successfully";
} catch (PDOException $e) {
    echo "Connection Failed: " . $e->getMessage();
} 