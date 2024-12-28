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
            <div class="col-md-8 mx-auto" id="posts-container">
                <!-- Posts will be loaded here by JavaScript -->
            </div>
            <div id="loading-spinner" class="text-center d-none">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>
    </div>

    <script src="../js/feed.js"></script>
</body>
</html>
