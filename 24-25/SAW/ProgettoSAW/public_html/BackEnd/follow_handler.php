<?php
require_once 'config_session.php';
require_once '../../dbh.php';

header('Content-Type: application/json');

if (!isset($_SESSION["user_id"])) {
    http_response_code(401);
    echo json_encode(['error' => 'Not logged in']);
    exit();
}

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON']);
    exit();
}

$followed_id = $data['userId'] ?? null;
$action = $data['action'] ?? null;

if (!$followed_id || !$action || !in_array($action, ['follow', 'unfollow'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid parameters']);
    exit();
}

if ($_SESSION["user_id"] == $followed_id) {
    http_response_code(400);
    echo json_encode(['error' => 'Cannot follow yourself']);
    exit();
}

try {
    if ($action === 'follow') {
        $stmt = $pdo->prepare("INSERT IGNORE INTO follows (follower_id, followed_id) VALUES (?, ?)");
    } else {
        $stmt = $pdo->prepare("DELETE FROM follows WHERE follower_id = ? AND followed_id = ?");
    }
    
    $stmt->execute([$_SESSION["user_id"], $followed_id]);
    
    if ($stmt->rowCount() > 0) {
        echo json_encode(['success' => true, 'action' => $action]);
    } else {
        echo json_encode(['success' => false, 'error' => 'No changes made']);
    }
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database error']);
}
