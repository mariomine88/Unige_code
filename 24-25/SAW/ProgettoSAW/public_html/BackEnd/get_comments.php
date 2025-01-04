<?php
// Prevent any unwanted output
error_reporting(E_ALL);
ini_set('display_errors', 0);

require_once __DIR__ . '/config_session.php';
require_once __DIR__ . '/../../dbh.php';

header('Content-Type: application/json');

if (!isset($_SESSION["user_id"])) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized']);
    exit();
}

$post_id = $_GET['post_id'] ?? null;
$page = isset($_GET['page']) ? (int)$_GET['page'] : 0;  // Changed to default to 0
$order = isset($_GET['order']) && $_GET['order'] === 'ASC' ? 'ASC' : 'DESC';
$limit = 10;
$offset = $page * $limit;  // Now correctly calculates offset from page 0

try {
    $stmt = $pdo->prepare("
        SELECT c.*, u.username, u.firstname, u.lastname 
        FROM comments c
        JOIN users u ON c.user_id = u.id 
        WHERE c.post_id = :post_id 
        ORDER BY c.created_at " . $order . "
        LIMIT :limit OFFSET :offset
    ");
    
    $stmt->bindValue(':post_id', $post_id, PDO::PARAM_INT);
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
    $stmt->execute();
    
    $comments = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode(['success' => true, 'data' => $comments]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database error', 'message' => $e->getMessage()]);
}
