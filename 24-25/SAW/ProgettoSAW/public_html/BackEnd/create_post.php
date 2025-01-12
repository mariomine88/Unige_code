<?php
require_once 'config_session.php';

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: ../pages/index.php");
    exit();
}

if (!isset($_SESSION["user_id"])) {
    header("Location: ../pages/login.php");
    exit();
}

$content = $_POST["content"] ?? "";
$title = $_POST["title"] ?? "";
$community_id = !empty($_POST["community_id"]) ? $_POST["community_id"] : null;

if (empty($content) || empty($title)) {
    $_SESSION["errors"]["post"] = "Post title and content cannot be empty";
    $_SESSION["data"] = [
        "content" => $content,
        "title" => $title
    ];
    header("Location: ../pages/create_post.php");
    exit();
}

if (strlen($title) > 255 || strlen($content) > 65535) {
    $_SESSION["errors"]["post"] = "Title or content exceeds maximum length";
    $_SESSION["data"] = [
        "content" => $content,
        "title" => $title
    ];
    header("Location: ../pages/create_post.php");
    exit();
}

try {
    require_once '../../dbh.php';
    $query = "INSERT INTO posts (user_id, community_id, title, content) VALUES (:user_id, :community_id, :title, :content)";
    $stmt = $pdo->prepare($query);
    $stmt->execute([
        ':user_id' => $_SESSION["user_id"],
        ':community_id' => $community_id,
        ':title' => $title,
        ':content' => $content
    ]);

    header("Location: ../pages/post.php?id=" . $pdo->lastInsertId());
    exit();
} catch (PDOException $e) {
    $_SESSION["errors"]["post"] = "Something went wrong. Please try again.";
    header("Location: ../pages/create_post.php");
    exit();
}

