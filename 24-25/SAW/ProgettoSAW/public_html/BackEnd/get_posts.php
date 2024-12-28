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

try {
    // Fetch posts with user information
    $stmt = $pdo->prepare("
        SELECT p.*, u.username 
        FROM posts p
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.created_at DESC 
        LIMIT :limit OFFSET :offset
    ");
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
    $stmt->execute();
    $posts = $stmt->fetchAll(PDO::FETCH_ASSOC);

    if (!$posts) {
        echo json_encode([]);
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
