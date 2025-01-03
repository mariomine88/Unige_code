<?php
require_once '../BackEnd/config_session.php';

// Redirect if not logged in
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
                <div class="card">
                    <div class="card-header">
                        <h2>Create New Post</h2>
                    </div>
                    <div class="card-body">
                        <form action="../BackEnd/create_post.php" method="post">
                            <div class="form-group">
                                <label for="title">Title</label>
                                <input type="text" class="form-control" id="title" name="title" maxlength="255" required>
                                <small class="text-muted">Characters remaining: <span id="titleCount">255</span></small>
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
        document.getElementById('title').addEventListener('input', function() {
            document.getElementById('titleCount').textContent = 255 - this.value.length;
        });
        document.getElementById('content').addEventListener('input', function() {
            document.getElementById('contentCount').textContent = 65535 - this.value.length;
        });
    </script>

    <?php include '../include/footer.php'; ?>
</body>
</html>
