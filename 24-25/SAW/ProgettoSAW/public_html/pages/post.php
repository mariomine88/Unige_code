<?php 
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php';

// Validate post ID
$post_id = $_GET['id'] ?? null;
if (!$post_id) {
    header("Location: errors_pages/404.php");
    die();
}

try {
    // Fetch post data
    $stmt = $pdo->prepare("
        SELECT p.*, u.username, u.firstname, u.lastname, c.name as community_name,
        CASE WHEN pl.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN community c ON p.community_id = c.id
        LEFT JOIN post_likes pl ON p.id = pl.post_id AND pl.user_id = ?
        WHERE p.id = ?
    ");
    $stmt->execute([
        $_SESSION["user_id"] ?? null,
        $post_id
    ]);
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
</head>
<body>
    <?php include '../include/navbar.php'; ?>

    <div class="container mt-5">
        <!-- Post Card -->
        <div class="card">
            <div class="card-body">
                <?php if ($post['community_name']): ?>
                    <div class="mb-2">
                        <a href="community_profile.php?name=<?php echo urlencode($post['community_name']); ?>" 
                           class="text-decoration-none">
                            <span class="badge bg-primary fs-6">
                                <i class="bi bi-people-fill me-1"></i>
                                <?php echo htmlspecialchars($post['community_name']); ?>
                            </span>
                        </a>
                    </div>
                <?php endif; ?>
                
                <h3><?php echo htmlspecialchars($post['title']); ?></h3>
                
                <!-- Post Meta -->
                <p class="text-muted">
                    Posted by <a href="public_profile.php?UID=<?php echo htmlspecialchars($post['username']); ?>">
                        <?php echo htmlspecialchars($post['username']); ?></a>
                    <?php if ($post['community_name']): ?>
                        in <a href="community_profile.php?name=<?php echo urlencode($post['community_name']); ?>">
                            <?php echo htmlspecialchars($post['community_name']); ?></a>
                    <?php endif; ?>
                    on <?php echo date('M d, Y H:i', strtotime($post['created_at'])); ?>
                </p>
                
                <!-- Post Content -->
                <div class="post-content mt-4">
                    <?php echo nl2br(htmlspecialchars($post['content'])); ?>
                </div>
                
                <!-- Like Button -->
                <div class="mt-3">
                    <button id="likeButton" class="btn me-2 <?php echo $post['is_liked'] ? 'btn-primary' : 'btn-outline-primary'; ?>">
                        <i class="bi bi-hand-thumbs-up"></i> Like
                        <span id="likeCount"><?php echo $post['like_count']; ?></span>
                    </button>
                    <button id="shareButton" class="btn btn-outline-secondary">
                        <i class="bi bi-share"></i> Share
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

            <!-- Alert Container -->
            <div id="alertContainer"></div>

            <!-- Comment Form -->
            <form id="commentForm" class="mb-4">
                <input type="hidden" name="post_id" value="<?php echo $post_id; ?>">
                <div class="form-group">
                    <textarea name="comment" class="form-control" rows="3" 
                        placeholder="Write a comment..." required maxlength="65535" id="commentText"></textarea>
                    <small class="text-muted">Characters remaining: <span id="commentCount">65535</span></small>
                </div>
                <button type="submit" class="btn btn-primary mt-2">
                <i class="bi bi-chat"></i> Comment
                </button>
            </form>

            <!-- Loading Spinner -->
            <div id="comments-loading-spinner" class="text-center mt-3 d-none">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading comments...</span>
                </div>
            </div>

            <div id="comments-container"></div>
        </div>
        <div class="mb-5"></div>
    </div>

    <script>
    const postData = {
        postId: <?php echo json_encode($post_id); ?>,
        isLiked: <?php echo json_encode((bool)$post['is_liked']); ?>
    };
    </script>
    <script type="module" src="../js/utils.js"></script>
    <script type="module" src="../js/likes.js"></script>
    <script type="module" src="../js/comments.js"></script>
    <script type="module" src="../js/post.js"></script>
</body>
</html>
