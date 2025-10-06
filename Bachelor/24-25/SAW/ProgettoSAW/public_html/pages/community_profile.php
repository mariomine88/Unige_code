<?php 
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php';

$community_name = $_GET['name'] ?? null;

if ($community_name === null) {
    header("Location: errors_pages/404.php");
    die();
}

try {
    $stmt = $pdo->prepare("SELECT * FROM community WHERE name = ?");
    $stmt->execute([$community_name]);
    $community = $stmt->fetch();

    if (!$community) {
        header("Location: errors_pages/404.php");
        die();
    }

    // Check if logged-in user is a member of this community
    $isMember = false;
    if (isset($_SESSION["user_id"])) {
        $checkMember = $pdo->prepare("SELECT 1 FROM community_members WHERE follower_id = ? AND community_id = ?");
        $checkMember->execute([$_SESSION["user_id"], $community['id']]);
        $isMember = $checkMember->fetch() !== false;
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
                <h3 class="card-title">
                    <?php echo htmlspecialchars($community['name']); ?>
                </h3>
                <p class="card-text"><?php echo htmlspecialchars($community['description']); ?></p>
                <p class="text-muted"><?php echo $community['member_count']; ?> Members</p>
                <p class="text-muted">Created: <?php echo date('F j, Y', strtotime($community['created_at'])); ?></p>
                
                <?php if (isset($_SESSION["user_id"])): ?>
                    <button id="joinButton" class="btn <?php echo $isMember ? 'btn-secondary' : 'btn-primary'; ?>">
                        <?php echo $isMember ? 'Leave Community' : 'Join Community'; ?>
                    </button>
                <?php endif; ?>
            </div>
        </div>

        <h3 class="mt-5 mb-4">Community Posts</h3>
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
        // Pass community data to JavaScript
        window.communityData = {
            name: <?php echo json_encode($community['name']); ?>,
            id: <?php echo json_encode($community['id']); ?>,
            isMember: <?php echo json_encode($isMember); ?>
        };
    </script>
    <script src="../js/community.js"></script>
</body>
</html>
