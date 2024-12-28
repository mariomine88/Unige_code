<?php
require_once '../BackEnd/config_session.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <h3 class="text-center mb-4">Sign Up</h3>
                
                <?php include '../include/messages.php'; ?>

                <form action="../BackEnd/registration.php" method="post">
                    <div class="row mb-3">
                        <div class="col">
                            <label for="firstname" class="form-label">First Name</label>
                            <input type="text" class="form-control" id="firstname" name="firstname" 
                                value="<?php echo isset($_SESSION["data"]["firstname"]) ? 
                                    htmlspecialchars($_SESSION["data"]["firstname"]) : ''; ?>" required>
                        </div>
                        <div class="col">
                            <label for="lastname" class="form-label">Last Name</label>
                            <input type="text" class="form-control" id="lastname" name="lastname" 
                                value="<?php echo isset($_SESSION["data"]["lastname"]) ? 
                                    htmlspecialchars($_SESSION["data"]["lastname"]) : ''; ?>" required>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" 
                            value="<?php echo isset($_SESSION["data"]["email"]) ? 
                                htmlspecialchars($_SESSION["data"]["email"]) : ''; ?>" required>
                    </div>
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" 
                            value="<?php echo isset($_SESSION["data"]["username"]) ? 
                                htmlspecialchars($_SESSION["data"]["username"]) : ''; ?>" required>
                    </div>
                    <div class="row mb-3">
                        <div class="col">
                            <label for="pwd" class="form-label">Password</label>
                            <input type="password" class="form-control" id="pwd" name="pass" required>
                        </div>
                        <div class="col">
                            <label for="cpwd" class="form-label">Confirm Password</label>
                            <input type="password" class="form-control" id="cpwd" name="cpwd" required>
                        </div>
                        <small class="form-text text-muted">
                                Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.
                        </small>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary">Sign Up</button>
                    </div>
                </form>
                
                <div class="text-center mt-3">
                    <button onclick="window.location.href='../index.php'" class="btn btn-secondary">Return Home</button>
                </div>
                
                <?php
                // Clear the session data after displaying it
                if (isset($_SESSION["data"])) {
                    unset($_SESSION["data"]);
                }
                ?>
            </div>
        </div>
    </div>
</body>
</html>