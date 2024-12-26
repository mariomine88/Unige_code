<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="index.php">YourBrand</a>
        <div class="ms-auto">
            <?php if (isset($_SESSION["user_username"])) : ?>
                <a href="../BackEnd/logout.php" class="btn btn-outline-danger">Logout</a>
                <a href="../BackEnd/show_profile.php" class="btn btn-outline-light me-2">Profile</a>
            <?php else : ?>
                <a href="../pages/signup.php" class="btn btn-outline-primary me-2">Sign Up</a>
                <a href="../pages/login.php" class="btn btn-primary">Login</a>
            <?php endif; ?>
        </div>
    </div>
</nav>
