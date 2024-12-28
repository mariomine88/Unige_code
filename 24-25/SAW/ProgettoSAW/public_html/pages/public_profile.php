<?php 
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php';

// Get user ID from URL
$user_id = $_GET['UID'] ?? null;

if ($user_id === null) {
    header("Location: errors_pages/404.php");
    die();
}

try {
    // Fetch user details from the database
    $stmt = $pdo->prepare("SELECT id, firstname, lastname, username, email FROM users WHERE username = ?");
    $stmt->execute([$user_id]);
    $user = $stmt->fetch();

    if (!$user) {
        header("Location: errors_pages/404.php");
        die();
    }

    // Fetch user posts from the database
    $stmt = $pdo->prepare("SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC");
    $stmt->execute([$user['id']]);
    $posts = $stmt->fetchAll();
} catch (PDOException $e) {
    header("Location: errors_pages/500.php");
    die();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
</head>
<body>
    <?php include '../include/navbar.php'; ?>

    <div class="container mt-5">
        <h2>Public Profile</h2>
        <div class="card">
            <div class="card-body">
                <h3 class="card-title"><?php echo htmlspecialchars($user['firstname'] . ' ' . $user['lastname']); ?></h3>
                <p class="card-text"><strong>Username:</strong> <?php echo htmlspecialchars($user['username']); ?></p>
            </div>
        </div>

        <h3 class="mt-5">Posts</h3>
        <?php if (count($posts) > 0): ?>
            <?php foreach ($posts as $post): ?>
                <div class="card mt-3">
                    <div class="card-body">
                        <h5 class="card-title"><?php echo htmlspecialchars($post['title']); ?></h5>
                        <p class="card-text"><?php echo nl2br(htmlspecialchars($post['content'])); ?></p>
                        <p class="card-text"><small class="text-muted">Posted on <?php echo htmlspecialchars($post['created_at']); ?></small></p>
                        
                        <!-- Comments Display -->
                        <div class="comments-section mt-3">
                            <?php
                            try {
                                $commentStmt = $pdo->prepare("
                                    SELECT comments.*, users.username 
                                    FROM comments 
                                    JOIN users ON comments.user_id = users.id 
                                    WHERE post_id = ? 
                                    ORDER BY created_at DESC
                                ");
                                $commentStmt->execute([$post['id']]);
                                $comments = $commentStmt->fetchAll();

                                if (count($comments) > 0) {
                                    foreach ($comments as $comment) {
                                        ?>
                                        <div class="comment border-bottom py-2">
                                            <div class="d-flex justify-content-between">
                                                <strong class="text-primary"><?php echo htmlspecialchars($comment['username']); ?></strong>
                                                <small class="text-muted"><?php echo date('M d, Y H:i', strtotime($comment['created_at'])); ?></small>
                                            </div>
                                            <p class="mb-1"><?php echo htmlspecialchars($comment['content']); ?></p>
                                        </div>
                                        <?php
                                    }
                                } else {
                                    echo '<p>No comments yet.</p>';
                                }
                            } catch (PDOException $e) {
                                echo '<div class="alert alert-warning">Comments temporarily unavailable</div>';
                            }
                            ?>
                        </div>

                        <!-- Add comment form -->
                        <form action="../BackEnd/add_comment.php" method="post" class="mt-3">
                            <input type="hidden" name="post_id" value="<?php echo $post['id']; ?>">
                            <div class="input-group">
                                <input type="text" name="comment" class="form-control" placeholder="Write a comment..." required>
                                <button type="submit" class="btn btn-primary">Comment</button>
                            </div>
                        </form>
                    </div>
                </div>
            <?php endforeach; ?>
        <?php else: ?>
            <p>No posts found.</p>
        <?php endif; ?>
    </div>

    <?php include '../include/footer.php'; ?>
</body>
</html>