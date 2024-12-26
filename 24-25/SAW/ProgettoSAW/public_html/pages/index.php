<?php require_once '../BackEnd/config_session.php'; ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
</head>
<body>
    <?php include '../include/navbar.php'; ?>

    <!-- Main Content -->
    <div class="container main-content">
        <?php if (isset($_SESSION["user_username"])) : ?>
            <h1>Welcome, <?php echo htmlspecialchars($_SESSION["user_username"]); ?>!</h1>
            <p class="lead">Thanks for being part of our community.</p>
        <?php else : ?>
            <h1>Welcome to Our Website</h1>
            <p class="lead">Join our community today!</p>
        <?php endif; ?>
    </div>

    <?php include '../include/footer.php'; ?>
</body>
</html>
