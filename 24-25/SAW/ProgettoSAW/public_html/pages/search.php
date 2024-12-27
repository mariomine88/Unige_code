<?php
require_once '../BackEnd/config_session.php';
require_once '../../dbh.php'; // Ensure this file contains the database connection setup

$searchTerm = '%' . ($_GET['search'] ?? '') . '%';

$sqlUsers = "SELECT * FROM users WHERE username LIKE ? OR firstname LIKE ? OR lastname LIKE ?";
$sqlPosts ="SELECT posts.*, users.username 
             FROM posts 
             JOIN users ON posts.user_id = users.id 
             WHERE posts.title LIKE ? OR posts.content LIKE ?";


$stmtUsers = $pdo->prepare($sqlUsers);
$stmtUsers->execute([$searchTerm, $searchTerm, $searchTerm]);
$resultUsers = $stmtUsers->fetchAll(PDO::FETCH_ASSOC);

$stmtPosts = $pdo->prepare($sqlPosts);
$stmtPosts->execute([$searchTerm, $searchTerm]);
$resultPosts = $stmtPosts->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
    <style>
        .tab {
            display: none;
        }
        .tab.active {
            display: block;
        }
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
        </div>

        <!-- Users Tab -->
        <div class="tab active" id="users">
            <?php if (empty($resultUsers)): ?>
                <div class="alert alert-info">No users found</div>
            <?php else: ?>
                <?php foreach ($resultUsers as $user): ?>
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">
                                <a href="public_profile.php?UID=<?= htmlspecialchars($user['username']) ?>">
                                    <?= htmlspecialchars($user['username']) ?>
                                </a>
                            </h5>
                            <p class="card-text">
                                <?= htmlspecialchars($user['firstname']) ?> <?= htmlspecialchars($user['lastname']) ?>
                            </p>
                        </div>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>

        <!-- Posts Tab -->
                <div class="tab" id="posts">
            <?php if (empty($resultPosts)): ?>
                <div class="alert alert-info">No posts found</div>
            <?php else: ?>
                <?php foreach ($resultPosts as $post): ?>
                    <div class="card mb-4">
                        <div class="card-body">
                            <h5 class="card-title"><?= htmlspecialchars($post['title']) ?></h5>
                            <h6 class="card-subtitle mb-2 text-muted">
                                By <a href="public_profile.php?UID=<?= htmlspecialchars($post['username']) ?>">
                                    <?= htmlspecialchars($post['username']) ?>
                                </a>
                            </h6>
                            <p class="card-text"><?= htmlspecialchars($post['content']) ?></p>
                            <p class="text-muted"><?= date('M d, Y H:i', strtotime($post['created_at'])) ?></p>
                        </div>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
    </div>

    <script>
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons and tabs
                document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked button and corresponding tab
                button.classList.add('active');
                document.getElementById(button.dataset.tab).classList.add('active');
            });
        });
    </script>

    <?php include '../include/footer.php'; ?>
</body>
</html>