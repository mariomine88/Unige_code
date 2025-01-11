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

// Handle both user follows and community memberships
$type = isset($data['communityId']) ? 'community' : 'user';
$targetId = $type === 'community' ? $data['communityId'] : $data['userId'];
$action = $data['action'] ?? null;

if (!$targetId || !$action) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid parameters']);
    exit();
}

try {
    if ($type === 'user') {
        // User follow/unfollow logic
        if ($_SESSION["user_id"] == $targetId) {
            http_response_code(400);
            echo json_encode(['error' => 'Cannot follow yourself']);
            exit();
        }

        if ($action === 'follow') {
            $stmt = $pdo->prepare("INSERT IGNORE INTO follows (follower_id, followed_id) VALUES (?, ?)");
        } else {
            $stmt = $pdo->prepare("DELETE FROM follows WHERE follower_id = ? AND followed_id = ?");
        }
        $stmt->execute([$_SESSION["user_id"], $targetId]);
    } else {
        // Community join/leave logic
        if ($action === 'join') {
            $stmt = $pdo->prepare("INSERT IGNORE INTO community_members (follower_id, community_id) VALUES (?, ?)");
            $stmt->execute([$_SESSION["user_id"], $targetId]);
            
            if ($stmt->rowCount() > 0) {
                $updateCount = $pdo->prepare("UPDATE community SET member_count = member_count + 1 WHERE id = ?");
                $updateCount->execute([$targetId]);
            }
        } else {
            $stmt = $pdo->prepare("DELETE FROM community_members WHERE follower_id = ? AND community_id = ?");
            $stmt->execute([$_SESSION["user_id"], $targetId]);
            
            if ($stmt->rowCount() > 0) {
                $updateCount = $pdo->prepare("UPDATE community SET member_count = GREATEST(member_count - 1, 0) WHERE id = ?");
                $updateCount->execute([$targetId]);
            }
        }
    }
    
    echo json_encode(['success' => true, 'action' => $action]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database error']);
}
