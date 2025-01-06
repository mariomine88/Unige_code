<?php
require_once __DIR__ . '/config_session.php';
require_once __DIR__ . '/../../dbh.php';

header('Content-Type: application/json');

if (!isset($_SESSION["user_id"])) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized']);
    exit();
}

$searchTerm = '%' . ($_GET['search'] ?? '') . '%';
$page = isset($_GET['page']) ? (int)$_GET['page'] : 0;
$limit = 10;
$offset = $page * $limit;

try {
    $stmt = $pdo->prepare("
        SELECT p.*, u.username, u.firstname, u.lastname, 
               (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count
        FROM posts p
        JOIN users u ON p.user_id = u.id 
        WHERE p.title LIKE :term 
        OR p.content LIKE :term
        OR u.firstname LIKE :term
        OR u.lastname LIKE :term
        ORDER BY p.created_at DESC
        LIMIT :limit OFFSET :offset
    ");
    
    $stmt->bindValue(':term', $searchTerm, PDO::PARAM_STR);
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
    $stmt->execute();
    
    $posts = $stmt->fetchAll(PDO::FETCH_ASSOC);
    echo json_encode(['success' => true, 'data' => $posts]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database error', 'message' => $e->getMessage()]);
}
