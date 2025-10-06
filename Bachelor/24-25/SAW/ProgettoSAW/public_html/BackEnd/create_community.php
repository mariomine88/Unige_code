<?php
require_once 'config_session.php';

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: ../pages/index.php");
    exit();
}

if (!isset($_SESSION["user_id"])) {
    header("Location: ../pages/login.php");
    exit();
}

if ($_SESSION["is_admin"] == 0) {
    header("Location: errors_pages/403.php");
    exit();
}

$name = $_POST["name"] ?? "";
$description = $_POST["description"] ?? "";

if (empty($name)) {
    $_SESSION["errors"]["community"] = "Community name cannot be empty";
    $_SESSION["data"] = [
        "name" => $name,
        "description" => $description
    ];
    header("Location: ../pages/create_community.php");
    exit();
}

if (strlen($name) > 100 || strlen($description) > 65535) {
    $_SESSION["errors"]["community"] = "Name or description exceeds maximum length";
    $_SESSION["data"] = [
        "name" => $name,
        "description" => $description
    ];
    header("Location: ../pages/create_community.php");
    exit();
}

try {
    require_once '../../dbh.php';
    $query = "INSERT INTO community (name, description) VALUES (:name, :description)";
    $stmt = $pdo->prepare($query);
    $stmt->execute([
        ':name' => $name,
        ':description' => $description
    ]);
    //redirect to the community profile after creating it successfully
    header("Location: ../pages/community_profile.php?name=" . urlencode($name));
    exit();
} catch (PDOException $e) {
    if ($e->getCode() == 23000) { // Duplicate entry error
        $_SESSION["errors"]["community"] = "A community with this name already exists";
    } else {
        $_SESSION["errors"]["community"] = "Something went wrong. Please try again.";
    }
    header("Location: ../pages/create_community.php");
    exit();
}
