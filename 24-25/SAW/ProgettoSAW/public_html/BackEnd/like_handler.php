<?php
require_once 'config_session.php';
require_once '../../dbh.php';

header('Content-Type: application/json');

if (!isset($_SESSION["user_id"])) {
    echo json_encode(["success" => false, "message" => "User not logged in"]);
    die();
}

$data = json_decode(file_get_contents('php://input'), true);
$userId = $_SESSION["user_id"];
$targetId = $data['targetId'] ?? null;
$action = $data['action'] ?? null;
$type = $data['type'] ?? null;

if (!$targetId || !$action || !$type || !in_array($action, ['like', 'unlike']) || !in_array($type, ['post', 'comment'])) {
    echo json_encode(["success" => false, "message" => "Invalid parameters"]);
    die();
}

try {
    if ($type === 'post') {
        $table = 'post_likes';
        $column = 'post_id';
        $updateTable = 'posts';
    } else {
        $table = 'comment_likes';
        $column = 'comment_id';
        $updateTable = 'comments';
    }

    if ($action === 'like') {
        $stmt = $pdo->prepare("INSERT IGNORE INTO $table (user_id, $column) VALUES (?, ?)");
    } else {
        $stmt = $pdo->prepare("DELETE FROM $table WHERE user_id = ? AND $column = ?");
    }
    
    $stmt->execute([$userId, $targetId]);

    // Update like count
    $countStmt = $pdo->prepare("SELECT COUNT(*) FROM $table WHERE $column = ?");
    $countStmt->execute([$targetId]);
    $likeCount = $countStmt->fetchColumn();

    // Update the like_count in the respective table
    $updateStmt = $pdo->prepare("UPDATE $updateTable SET like_count = ? WHERE id = ?");
    $updateStmt->execute([$likeCount, $targetId]);

    echo json_encode([
        "success" => true,
        "likeCount" => $likeCount
    ]);
} catch (PDOException $e) {
    echo json_encode(["success" => false, "message" => "Database error"]);
}
