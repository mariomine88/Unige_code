<?php
require_once '../BackEnd/config_session.php';

if (!isset($_SESSION["user_id"])) {
    header("Location: login.php");
    exit();
}

if ($_SESSION["is_admin"] == 0) {
    header("Location: errors_pages/403.php");
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
                        <h2>Create New Community</h2>
                    </div>
                    <div class="card-body">
                        <?php include '../include/messages.php'; ?>
                        <form action="../BackEnd/create_community.php" method="post">
                            <div class="form-group">
                                <label for="name">Community Name</label>
                                <input type="text" class="form-control" id="name" name="name" maxlength="100" required>
                                <small class="text-muted">Characters remaining: <span id="nameCount">100</span></small>
                            </div>
                            <div class="form-group mt-3">
                                <label for="description">Description</label>
                                <textarea class="form-control" id="description" name="description" rows="4" maxlength="65535"></textarea>
                                <small class="text-muted">Characters remaining: <span id="descriptionCount">65535</span></small>
                            </div>
                            <button type="submit" class="btn btn-primary mt-3">Create Community</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('name').addEventListener('input', function() {
            document.getElementById('nameCount').textContent = 100 - this.value.length;
        });
        document.getElementById('description').addEventListener('input', function() {
            document.getElementById('descriptionCount').textContent = 65535 - this.value.length;
        });
    </script>

    <?php include '../include/footer.php'; ?>
</body>
</html>
