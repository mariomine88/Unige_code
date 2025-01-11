<?php
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php';

$searchTerm = $_GET['search'] ?? '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
    <style>
        .tab { display: none; }
        .tab.active { display: block; }
        .tab-button.active {
            background-color: #007bff;
            color: white;
        }
    </style>
</head>
<body>
    <?php include '../include/navbar.php'; ?>

    <div class="container mt-4">
        <div class="btn-group mb-4" role="group">
            <button type="button" class="btn btn-outline-primary tab-button active" data-tab="users">Users</button>
            <button type="button" class="btn btn-outline-primary tab-button" data-tab="posts">Posts</button>
            <button type="button" class="btn btn-outline-primary tab-button" data-tab="communities">Communities</button>
        </div>

        <!-- Users Tab -->
        <div class="tab active" id="users">
            <div id="users-container"></div>
            <div id="users-loading" class="text-center d-none">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>

        <!-- Posts Tab -->
        <div class="tab" id="posts">
            <div id="posts-container"></div>
            <div id="posts-loading" class="text-center d-none">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>

        <!-- Communities Tab -->
        <div class="tab" id="communities">
            <div id="communities-container"></div>
            <div id="communities-loading" class="text-center d-none">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        window.searchData = {
            term: <?php echo json_encode($searchTerm); ?>
        };
    </script>
    <script src="../js/search.js"></script>
</body>
</html>