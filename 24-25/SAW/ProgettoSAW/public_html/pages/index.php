<?php require_once '../BackEnd/config_session.php'; ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
    <style>
        .hero-section {
            padding: 100px 0;
            text-align: center;
            background-color:rgb(255, 255, 255);
        }
        .cta-button {
            margin-top: 20px;
            padding: 10px 30px;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <?php include '../include/navbar.php'; ?>

    <div class="hero-section">
        <div class="container">
            <?php if (isset($_SESSION["user_username"])) : ?>
                <h1 class="display-4">Welcome Back, <?php echo htmlspecialchars($_SESSION["user_username"]); ?>!</h1>
                <p class="lead">See what's new in your feed today.</p>
                <a href="feed.php" class="btn btn-primary btn-lg cta-button" aria-label="Go to Feed">Go to Feed</a>
            <?php else : ?>
                <h1 class="display-4">Connect with People</h1>
                <p class="lead">Join our community to share your thoughts and engage with others.</p>
                <a href="signup.php" class="btn btn-primary btn-lg cta-button" aria-label="Join Threadit">Join Threadit!</a>
            <?php endif; ?>
        </div>
    </div>

    <div class="container mt-5">
        <div class="row">
            <div class="col-md-4 text-center">
                <h2>Share</h2>
                <p>Share your thoughts with the community</p>
            </div>
            <div class="col-md-4 text-center">
                <h2>Connect</h2>
                <p>Connect with like-minded people</p>
            </div>
            <div class="col-md-4 text-center">
                <h2>Engage</h2>
                <p>Engage in meaningful conversations</p>
            </div>
        </div>
    </div>

    <?php include '../include/footer.php'; ?>
</body>
</html>
