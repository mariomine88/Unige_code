<?php

$host= 'localhost';    // Host Name
$dbname = 'sawdb';    // Database Name
$dns = 'mysql:host='.$host.'localhost;dbname='.$dbname;    // Data Source
$dbusername = "root";    // Database Username
$dbpassword = "";    // Database Password
$dns = 'mysql:host=localhost;dbname=sawdb';    // Data Source

try {
    $pdo = new PDO($dns, $dbusername, $dbpassword);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    header("Location: ../pages/errors_pages/500.php");
    die();
}