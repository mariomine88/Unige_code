<?php
require_once 'config_session.php';
require_once '../../dbh.php';

header('Content-Type: application/json');

if (!isset($_SESSION["user_id"])) {
    echo json_encode(["success" => false, "message" => "Please login to comment"]);
    exit();
}

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    echo json_encode(["success" => false, "message" => "Invalid request method"]);
    exit();
}

$post_id = $_POST["post_id"] ?? null;
$comment = $_POST["comment"] ?? null;

if (!$post_id || !$comment) {
    echo json_encode(["success" => false, "message" => "Missing required fields"]);
    exit();
}

try {
    $stmt = $pdo->prepare("INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)");
    $success = $stmt->execute([$post_id, $_SESSION["user_id"], $comment]);

    if ($success) {
        echo json_encode(["success" => true]);
    } else {
        echo json_encode(["success" => false, "message" => "Failed to add comment"]);
    }
} catch (PDOException $e) {
    echo json_encode(["success" => false, "message" => "Database error"]);
}

