<?php
require_once 'config_session.php';

// move add coment to js

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: ../pages/feed.php");
    exit();
}


if (!isset($_SESSION["user_id"])) {
    header("Location: ../pages/login.php");
    exit();
}

$comment = $_POST["comment"] ?? "";
$post_id = $_POST["post_id"] ?? "";

if (empty($comment) || empty($post_id)) {
    $_SESSION["errors"]["comment"] = "Comment cannot be empty";
    header("Location: ../pages/feed.php");
    exit();
}

if (strlen($comment) > 65535) {
    $_SESSION["errors"]["comment"] = "Comment exceeds maximum length";
    header("Location: ../pages/feed.php");
    exit();
}

try {
    require_once '../../dbh.php';
    $query = "INSERT INTO comments (post_id, user_id, content) VALUES (:post_id, :user_id, :content)";
    $stmt = $pdo->prepare($query);
    $stmt->execute([
        ':post_id' => $post_id,
        ':user_id' => $_SESSION["user_id"],
        ':content' => $comment
    ]);

    header("Location: ../pages/feed.php");
    exit();
} catch (PDOException $e) {
    header("Location: ../pages/errors_pages/500.php");
    exit();
}

