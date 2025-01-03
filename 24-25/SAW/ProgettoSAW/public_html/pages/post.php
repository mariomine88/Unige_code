<?php 
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php';

// Get post ID from URL
$post_id = $_GET['id'] ?? null;

if ($post_id === null) {
    header("Location: errors_pages/404.php");
    die();
}

try {
    // Fetch post details with user and community information
    $stmt = $pdo->prepare("
        SELECT p.*, u.username, u.firstname, u.lastname, c.name as community_name 
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN community c ON p.community_id = c.id
        WHERE p.id = ?
    ");
    $stmt->execute([$post_id]);
    $post = $stmt->fetch();

    if (!$post) {
        header("Location: errors_pages/404.php");
        die();
    }
} catch (PDOException $e) {
    header("Location: errors_pages/500.php");
    die();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
</head>
<body>
    <?php include '../include/navbar.php'; ?>

    <div class="container mt-5">
        <div class="card">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <h3 class="card-title"><?php echo htmlspecialchars($post['title']); ?></h3>
                    <?php if ($post['community_name']): ?>
                        <span class="badge bg-secondary">
                            <?php echo htmlspecialchars($post['community_name']); ?>
                        </span>
                    <?php endif; ?>
                </div>
                <p class="text-muted">
                    Posted by 
                    <a href="public_profile.php?UID=<?php echo htmlspecialchars($post['username']); ?>">
                        <?php echo htmlspecialchars($post['firstname'] . ' ' . $post['lastname']); ?>
                    </a>
                    on <?php echo date('M d, Y H:i', strtotime($post['created_at'])); ?>
                </p>
                <div class="post-content mt-4">
                    <?php echo nl2br(htmlspecialchars($post['content'])); ?>
                </div>
                
                <!-- Like Button -->
                <div class="mt-3">
                    <?php
                    $isLiked = false;
                    if (isset($_SESSION["user_id"])) {
                        // Updated query to use post_likes table
                        $likeStmt = $pdo->prepare("SELECT * FROM post_likes WHERE user_id = ? AND post_id = ?");
                        $likeStmt->execute([$_SESSION["user_id"], $post_id]);
                        $isLiked = $likeStmt->rowCount() > 0;
                    }
                    
                    // Get like count directly from posts table since it's maintained by triggers
                    $likeCount = $post['like_count'];
                    ?>
                    
                    <button id="likeButton" class="btn <?php echo $isLiked ? 'btn-primary' : 'btn-outline-primary'; ?>">
                        <i class="bi bi-hand-thumbs-up"></i>
                        Like
                        <span id="likeCount"><?php echo $likeCount; ?></span>
                    </button>
                </div>
            </div>
        </div>

        <!-- Comments Section -->
        <div class="comments-section mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4>Comments</h4>
                <select id="commentOrder" class="form-select" style="width: auto;">
                    <option value="DESC">Newest First</option>
                    <option value="ASC">Oldest First</option>
                </select>
            </div>

            <!-- Add comment form -->
            <form action="../BackEnd/add_comment.php" method="post" class="mb-4">
                <input type="hidden" name="post_id" value="<?php echo $post_id; ?>">
                <div class="form-group">
                    <textarea name="comment" class="form-control" rows="3" 
                        placeholder="Write a comment..." required maxlength="65535" id="commentText"></textarea>
                    <small class="text-muted">Characters remaining: <span id="commentCount">65535</span></small>
                </div>
                <button type="submit" class="btn btn-primary mt-2">Add Comment</button>
            </form>

            <div id="comments-container">
            <?php
            try {
                $order = isset($_GET['order']) ? $_GET['order'] : 'DESC';
                $order = in_array($order, ['ASC', 'DESC']) ? $order : 'DESC';
                
                $commentStmt = $pdo->prepare("
                    SELECT c.*, u.username, u.firstname, u.lastname 
                    FROM comments c
                    JOIN users u ON c.user_id = u.id 
                    WHERE c.post_id = ? 
                    ORDER BY c.created_at " . $order . "
                    LIMIT 10"
                );
                $commentStmt->execute([$post_id]);
                $comments = $commentStmt->fetchAll();

                if (count($comments) > 0) {
                    foreach ($comments as $comment) {
                        ?>
                        <div class="comment card mt-2">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <strong class="text-primary">
                                            <a href="public_profile.php?UID=<?php echo htmlspecialchars($comment['username']); ?>">
                                                <?php echo htmlspecialchars($comment['firstname'] . ' ' . $comment['lastname']); ?>
                                            </a>
                                        </strong>
                                        <small class="text-muted ms-2">
                                            @<?php echo htmlspecialchars($comment['username']); ?>
                                        </small>
                                    </div>
                                    <small class="text-muted">
                                        <?php echo date('M d, Y H:i', strtotime($comment['created_at'])); ?>
                                    </small>
                                </div>
                                <p class="mt-2 mb-1"><?php echo htmlspecialchars($comment['content']); ?></p>
                            </div>
                        </div>
                        <?php
                    }
                } else {
                    echo '<p class="text-muted">No comments yet. Be the first to comment!</p>';
                }
            } catch (PDOException $e) {
                echo '<div class="alert alert-warning">Comments temporarily unavailable</div>';
            }
            ?>
            </div>
            <div class="text-center mt-3" id="load-more-container">
                <button id="loadMoreComments" class="btn btn-outline-primary">Load More Comments</button>
            </div>
        </div>
    </div>

    <script>
        window.postData = {
            postId: <?php echo json_encode($post_id); ?>,
            isLiked: <?php echo json_encode($isLiked); ?>
        };
    </script>
    <script src="../js/post.js"></script>
    <script src="../js/likes.js"></script>
    <script>
        document.getElementById('commentText').addEventListener('input', function() {
            document.getElementById('commentCount').textContent = 65535 - this.value.length;
        });
    </script>
</body>
</html>
