<?php 
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php';

$user_id = $_GET['UID'] ?? null;

if ($user_id === null) {
    header("Location: errors_pages/404.php");
    die();
}

try {
    $stmt = $pdo->prepare("SELECT id, firstname, lastname, username FROM users WHERE username = ?");
    $stmt->execute([$user_id]);
    $user = $stmt->fetch();

    if (!$user) {
        header("Location: errors_pages/404.php");
        die();
    }

    // Check if logged-in user is following this profile
    $isFollowing = false;
    if (isset($_SESSION["user_id"])) {
        $checkFollow = $pdo->prepare("SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = ?");
        $checkFollow->execute([$_SESSION["user_id"], $user['id']]);
        $isFollowing = $checkFollow->fetch() !== false;
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
        <div class="card mb-4">
            <div class="card-body">
                <h3 class="card-title"><?php echo htmlspecialchars($user['firstname'] . ' ' . $user['lastname']); ?></h3>
                <p class="card-text"><strong>Username:</strong> <?php echo htmlspecialchars($user['username']); ?></p>
                <?php if (isset($_SESSION["user_id"]) && $_SESSION["user_id"] !== $user['id']): ?>
                    <button id="followButton" class="btn <?php echo $isFollowing ? 'btn-secondary' : 'btn-primary'; ?>">
                        <?php echo $isFollowing ? 'Unfollow' : 'Follow'; ?>
                    </button>
                <?php endif; ?>
            </div>
        </div>

        <h3 class="mt-5 mb-4">Posts</h3>
        <div id="posts-container">
            <!-- Posts will be loaded here by JavaScript -->
        </div>
        <div class="text-center mt-3" id="load-more-container">
            <button id="loadMorePosts" class="btn btn-outline-primary">Load More Posts</button>
        </div>
        <div id="loading-spinner" class="text-center d-none">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    </div>

    <script>
        // Pass user data to JavaScript
        window.userData = {
            username: <?php echo json_encode($user['username']); ?>,
            userId: <?php echo json_encode($user['id']); ?>,
            isFollowing: <?php echo json_encode($isFollowing); ?>
        };
    </script>
    <script src="../js/profile.js"></script>
</body>
</html>