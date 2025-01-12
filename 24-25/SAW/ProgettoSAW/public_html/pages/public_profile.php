<?php 
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php';

$user_id = $_GET['UID'] ?? null;

if ($user_id === null) {
    header("Location: errors_pages/404.php");
    die();
}

try {
    $stmt = $pdo->prepare("SELECT id, firstname, lastname, username, is_admin FROM users WHERE username = ?");
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

    // Get followers count
    $stmt = $pdo->prepare("SELECT COUNT(*) AS followers_count FROM follows WHERE followed_id = ?");
    $stmt->execute([$user['id']]);
    $followers_count = $stmt->fetchColumn();
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
            <div class="card-body position-relative">
                <?php if (isset($_SESSION['is_admin']) && $_SESSION['is_admin']): ?>
                    <div class="dropdown position-absolute top-0 end-0 mt-2 me-2">
                        <button class="btn btn-secondary dropdown-toggle" type="button" id="adminActions" data-bs-toggle="dropdown" aria-expanded="false">
                            &#x22EE;
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="adminActions">
                            <li><a class="dropdown-item admin-action" href="#" data-action="mute">Mute</a></li>
                            <li><a class="dropdown-item admin-action" href="#" data-action="ban">Ban</a></li>
                            <li><a class="dropdown-item admin-action" href="#" data-action="delete">Delete Account</a></li>
                        </ul>
                    </div>
                <?php endif; ?>
                <?php $adminBadge = $user['is_admin'] ? '<span class="badge bg-primary AdminBadge">Admin</span>' : ''; ?>
                <h3 class="card-title">
                    <?php echo htmlspecialchars($user['firstname'] . ' ' . $user['lastname']) . ' ' . $adminBadge; ?>
                </h3>
                <p class="card-text"><strong>Username:</strong> <?php echo htmlspecialchars($user['username']); ?></p>
                <p class="text-muted"><?php echo $followers_count; ?> Followers</p>
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

        document.querySelectorAll('.admin-action').forEach(item => {
            item.addEventListener('click', event => {
                event.preventDefault();
                const action = event.target.getAttribute('data-action');
                alert(`Admin action: ${action}`);
            });
        });
    </script>
    <script src="../js/profile.js"></script>
</body>
</html>