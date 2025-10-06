<?php
require_once 'config_session.php';
require_once '../../dbh.php';

// Check if accessed directly via URL using AJAX
if (!isset($_SERVER['HTTP_X_REQUESTED_WITH']) || strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) != 'xmlhttprequest') {
    http_response_code(403);
    echo json_encode(['error' => 'Direct access not allowed']);
    exit();
}

header('Content-Type: application/json');

if (!isset($_SESSION["user_id"])) {
    http_response_code(401);
    echo json_encode(['error' => 'Not logged in']);
    exit();
}

$query = '%' . ($_GET['search'] ?? '') . '%';
$page = isset($_GET['page']) ? (int)$_GET['page'] : 0;
$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 5;
$offset = $page * $limit;

if (strlen($query) < 2) {
    echo json_encode(['success' => true, 'communities' => []]);
    exit();
}

try {
    $stmt = $pdo->prepare("
        SELECT id, name, description, member_count, created_at 
        FROM community 
        WHERE name LIKE :query
        ORDER BY member_count DESC, name ASC
        LIMIT :limit OFFSET :offset
    ");
    
    $stmt->bindValue(':query', $query, PDO::PARAM_STR);
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
    $stmt->execute();
    
    $communities = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode(['success' => true, 'data' => $communities]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database error']);
}
