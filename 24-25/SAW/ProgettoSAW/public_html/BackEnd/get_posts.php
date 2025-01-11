<?php
require_once __DIR__ . '/config_session.php';
require_once __DIR__ . '/../../dbh.php';

header('Content-Type: application/json');

if (!isset($_SESSION["user_id"])) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized']);
    exit();
}

$page = isset($_GET['page']) ? (int)$_GET['page'] : 0;
$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 10;
$offset = $page * $limit;
$specific_user_id = $_GET['user_id'] ?? null;
$community_id = $_GET['community_id'] ?? null;

try {
    if ($specific_user_id) {
        // Query for specific user's posts
        $stmt = $pdo->prepare("
            SELECT p.*, u.username, c.name as community_name,
                   (SELECT COUNT(*) FROM comments cm WHERE cm.post_id = p.id) AS comment_count
            FROM posts p
            INNER JOIN users u ON p.user_id = u.id
            LEFT JOIN community c ON p.community_id = c.id
            WHERE p.user_id = :specific_user_id 
            ORDER BY p.created_at DESC 
            LIMIT :limit OFFSET :offset
        ");
        $stmt->bindValue(':specific_user_id', $specific_user_id, PDO::PARAM_INT);
    } elseif ($community_id) {
        // Query for community posts
        $stmt = $pdo->prepare("
            SELECT p.*, u.username, c.name as community_name,
                   (SELECT COUNT(*) FROM comments cm WHERE cm.post_id = p.id) AS comment_count
            FROM posts p
            INNER JOIN users u ON p.user_id = u.id
            LEFT JOIN community c ON p.community_id = c.id
            WHERE p.community_id = :community_id
            ORDER BY p.created_at DESC 
            LIMIT :limit OFFSET :offset
        ");
        $stmt->bindValue(':community_id', $community_id, PDO::PARAM_INT);
    } else {
        // Query for feed posts
        $stmt = $pdo->prepare("
            SELECT DISTINCT p.*, u.username, c.name as community_name,
                   (SELECT COUNT(*) FROM comments cm WHERE cm.post_id = p.id) AS comment_count 
            FROM posts p
            INNER JOIN users u ON p.user_id = u.id
            LEFT JOIN community c ON p.community_id = c.id
            INNER JOIN follows f ON f.followed_id = p.user_id
            WHERE f.follower_id = :user_id 
            AND p.user_id != :user_id
            ORDER BY p.created_at DESC 
            LIMIT :limit OFFSET :offset
        ");
        $stmt->bindValue(':user_id', $_SESSION["user_id"], PDO::PARAM_INT);
    }
    
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
    $stmt->execute();
    $posts = $stmt->fetchAll(PDO::FETCH_ASSOC);

    if (!$posts) {
        echo json_encode(['success' => true, 'data' => []]);
        exit();
    }

    // Fetch 3 most recent comments for each post
    foreach ($posts as &$post) {
        $commentStmt = $pdo->prepare("
            SELECT c.*, u.username 
            FROM comments c
            JOIN users u ON c.user_id = u.id 
            WHERE c.post_id = :post_id 
            ORDER BY c.created_at DESC 
            LIMIT 3
        ");
        $commentStmt->bindValue(':post_id', $post['id'], PDO::PARAM_INT);
        $commentStmt->execute();
        $post['comments'] = $commentStmt->fetchAll(PDO::FETCH_ASSOC);
    }

    echo json_encode(['success' => true, 'data' => $posts]);
} catch (PDOException $e) {
    error_log("Database Error: " . $e->getMessage());
    http_response_code(500);
    echo json_encode(['error' => 'Database error', 'message' => $e->getMessage()]);
}
