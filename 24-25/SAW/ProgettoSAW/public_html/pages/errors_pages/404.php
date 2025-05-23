<?php
require_once '../../BackEnd/config_session.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../../include/header.php'; ?>
    <title>404 Error</title>
</head>
<body>
    <div class="container mt-5 text-center">
        <h1>404 - Page Not Found</h1>
        <?php if (isset($_SESSION['error_message'])): ?>
            <div class="alert alert-danger">
                <?php echo htmlspecialchars($_SESSION['error_message']); ?>
            </div>
        <?php endif; ?>
        <a href="../../index.php" class="btn btn-primary">Home</a>
    </div>
    <?php unset($_SESSION['error_message']); ?>
</body>
</html>
