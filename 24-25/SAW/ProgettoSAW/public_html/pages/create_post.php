<?php
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php';

// Redirect if not logged in
if (!isset($_SESSION["user_id"])) {
    header("Location: login.php");
    exit();
}

// Get pre-selected community if specified
$community_name = $_GET['community_name'] ?? null;
$community_data = null;

if ($community_name) {
    try {
        $stmt = $pdo->prepare("SELECT id, name FROM community WHERE name = ?");
        $stmt->execute([$community_name]);
        $community_data = $stmt->fetch(PDO::FETCH_ASSOC);
    } catch (PDOException $e) {
        // Silently fail - community selection will just be empty
    }
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
                <div class="card">
                    <div class="card-header">
                        <h2>Create New Post</h2>
                    </div>
                    <div class="card-body">
                        <?php include '../include/messages.php'; ?>
                        <form action="../BackEnd/create_post.php" method="post" id="createPostForm">
                            <div class="form-group">
                                <label for="title">Title</label>
                                <input type="text" class="form-control" id="title" name="title" maxlength="255" required>
                                <small class="text-muted">Characters remaining: <span id="titleCount">255</span></small>
                            </div>
                            
                            <div class="form-group mt-3">
                                <label for="communitySearch">Post in Community (optional)</label>
                                <div class="community-search-wrapper position-relative">
                                    <div class="input-group">
                                        <input type="text" 
                                               class="form-control" 
                                               id="communitySearch" 
                                               placeholder="Start typing to search communities (min. 2 characters)..."
                                               autocomplete="off">
                                        <input type="hidden" id="communityId" name="community_id">
                                        <button class="btn btn-outline-secondary" type="button" id="clearCommunity">×</button>
                                    </div>
                                    <div id="communityResults" class="list-group mt-2 d-none"></div>
                                    <small id="selectedCommunity" class="text-muted"></small>
                                </div>
                            </div>

                            <div class="form-group mt-3">
                                <label for="content">What's on your mind?</label>
                                <textarea class="form-control" id="content" name="content" rows="4" maxlength="65535" required></textarea>
                                <small class="text-muted">Characters remaining: <span id="contentCount">65535</span></small>
                            </div>
                            <button type="submit" class="btn btn-primary mt-3">Post</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Pass pre-selected community data to JavaScript
        <?php if ($community_data): ?>
        window.preSelectedCommunity = {
            id: <?php echo json_encode($community_data['id']); ?>,
            name: <?php echo json_encode($community_data['name']); ?>
        };
        <?php endif; ?>

        document.getElementById('title').addEventListener('input', function() {
            document.getElementById('titleCount').textContent = 255 - this.value.length;
        });
        document.getElementById('content').addEventListener('input', function() {
            document.getElementById('contentCount').textContent = 65535 - this.value.length;
        });
    </script>
    <script src="../js/create_post.js"></script>

    <?php include '../include/footer.php'; ?>
</body>
</html>
