<?php
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php';

if (!isset($_SESSION["user_id"])) {
    header("Location: login.php");
    exit();
}

// Check if user follows anyone or any community
$stmt = $pdo->prepare("
    SELECT 
        (SELECT COUNT(*) FROM follows WHERE follower_id = ?) +
        (SELECT COUNT(*) FROM community_members WHERE follower_id = ?)
");
$stmt->execute([$_SESSION["user_id"], $_SESSION["user_id"]]);
$followCount = $stmt->fetchColumn();
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
                <?php if ($followCount == 0): ?>
                    <div class="text-center p-5">
                        <h3>Welcome to Your Feed!</h3>
                        <p class="lead mb-4">You're not following anyone yet. Start following other profiles to see their posts here.</p>
                        <a href="../pages/search.php?search=" 
                           class="btn btn-primary btn-lg">
                            Find People to Follow
                        </a>
                    </div>
                <?php else: ?>
                    <div id="posts-container">
                        <!-- Posts will be loaded here -->
                    </div>
                    <div id="loading-spinner" class="text-center">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <script>
        window.hasFollows = <?php echo json_encode($followCount > 0); ?>;
    </script>
    <script src="../js/feed.js"></script>
</body>
</html>
