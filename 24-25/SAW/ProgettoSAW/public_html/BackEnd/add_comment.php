<?php
require_once 'config_session.php';

if ($_SERVER["REQUEST_METHOD"] === "POST") {
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
        $_SESSION["errors"]["comment"] = "Something went wrong. Please try again.";
        header("Location: ../pages/errors/500.php");
        exit();
    }
} else {
    header("Location: ../pages/feed.php");
    exit();
}
