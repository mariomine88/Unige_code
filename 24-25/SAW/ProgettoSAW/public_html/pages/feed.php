<?php
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php';

if (!isset($_SESSION["user_id"])) {
    header("Location: login.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
</head>
<body>
    <?php include '../include/navbar.php'; ?>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8 mx-auto">
                
                <?php
                try {
                    // Fetch all posts
                    $stmt = $pdo->query("SELECT posts.*, users.username 
                                       FROM posts 
                                       JOIN users ON posts.user_id = users.id 
                                       ORDER BY created_at DESC");
                    
                    while ($post = $stmt->fetch()) {
                        ?>
                        <div class="card mb-4">
                            <div class="card-body">
                                <h5 class="card-title"><?= htmlspecialchars($post['title']) ?></h5>
                                <h6 class="card-subtitle mb-2 text-muted">
                                    By <a href="https://saw.dibris.unige.it/~s5577783/pages/public_profile.php?UID=<?= htmlspecialchars($post['username']) ?>" class="text-muted"><?= htmlspecialchars($post['username']) ?></a>
                                </h6>                                
                                <p class="card-text"><?= htmlspecialchars($post['content']) ?></p>
                                <p class="text-muted"><?= date('M d, Y H:i', strtotime($post['created_at'])) ?></p>
                                
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
                                        
                                        while ($comment = $commentStmt->fetch()) {
                                            ?>
                                            <div class="comment border-bottom py-2">
                                                <div class="d-flex justify-content-between">
                                                    <strong class="text-primary"><?= htmlspecialchars($comment['username']) ?></strong>
                                                    <small class="text-muted"><?= date('M d, Y H:i', strtotime($comment['created_at'])) ?></small>
                                                </div>
                                                <p class="mb-1"><?= htmlspecialchars($comment['content']) ?></p>
                                            </div>
                                            <?php
                                        }
                                    } catch (PDOException $e) {
                                        // Silently handle comment loading errors
                                        echo '<div class="alert alert-warning">Comments temporarily unavailable</div>';
                                    }
                                    ?>
                                </div>

                                <!-- Add comment form -->
                                <form action="../BackEnd/add_comment.php" method="post" class="mt-3">
                                    <input type="hidden" name="post_id" value="<?= $post['id'] ?>">
                                    <div class="input-group">
                                        <input type="text" name="comment" class="form-control" placeholder="Write a comment..." required>
                                        <button type="submit" class="btn btn-primary">Comment</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                        <?php
                    }
                } catch (PDOException $e) {
                    if ($e->getCode() == '42S02') { // Table doesn't exist error
                        echo '<div class="alert alert-warning">
                                No posts available at the moment. Please try again later.
                              </div>';
                    } else {
                        echo '<div class="alert alert-danger">
                                An error occurred while loading posts. Please try again later.
                              </div>';
                    }
                }
                ?>
            </div>
        </div>
    </div>

    <?php include '../include/footer.php'; ?>
</body>
</html>
