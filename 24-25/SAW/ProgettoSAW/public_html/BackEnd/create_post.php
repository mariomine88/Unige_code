<?php
require_once 'config_session.php';

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    if (!isset($_SESSION["user_id"])) {
        header("Location: ../pages/login.php");
        exit();
    }

    $content = $_POST["content"] ?? "";
    $title = $_POST["title"] ?? "";

    if (empty($content) || empty($title)) {
        $_SESSION["errors"]["post"] = "Post title and content cannot be empty";
        header("Location: ../pages/create_post.php");
        exit();
    }

    try {
        require_once '../../dbh.php';
        $query = "INSERT INTO posts (user_id, title, content) VALUES (:user_id, :title, :content)";
        $stmt = $pdo->prepare($query);
        $stmt->execute([
            ':user_id' => $_SESSION["user_id"],
            ':title' => $title,
            ':content' => $content
        ]);

        header("Location: ../pages/feed.php");
        exit();
    } catch (PDOException $e) {
        $_SESSION["errors"]["post"] = "Something went wrong. Please try again.";
        header("Location: ../pages/create_post.php");
        exit();
    }
} else {
    header("Location: ../pages/feed.php");
    exit();
}
