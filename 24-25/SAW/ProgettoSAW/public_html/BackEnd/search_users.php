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
        SELECT * FROM users 
        WHERE username LIKE :term 
        OR firstname LIKE :term 
        OR lastname LIKE :term
        LIMIT :limit OFFSET :offset
    ");
    
    $stmt->bindValue(':term', $searchTerm, PDO::PARAM_STR);
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
    $stmt->execute();
    
    $users = $stmt->fetchAll(PDO::FETCH_ASSOC);
    echo json_encode(['success' => true, 'data' => $users]);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database error', 'message' => $e->getMessage()]);
}
