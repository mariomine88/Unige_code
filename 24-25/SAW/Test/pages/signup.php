<?php
require_once '../backend/config_session.php';
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
                
                <?php
                if (isset($_SESSION["signup_errors"]) && !empty($_SESSION["signup_errors"])) {
                    foreach ($_SESSION["signup_errors"] as $error) {
                        echo '<div class="alert alert-danger" role="alert">' . htmlspecialchars($error) . '</div>';
                    }
                    unset($_SESSION["signup_errors"]);
                }
                
                if (isset($_SESSION["signup_success"])) {
                    echo '<div class="alert alert-success" role="alert">' . htmlspecialchars($_SESSION["signup_success"]) . '</div>';
                    unset($_SESSION["signup_success"]);
                }
                ?>

                <form action="../backend/signuphandlere.php" method="post">
                    <div class="row mb-3">
                        <div class="col">
                            <label for="firstname" class="form-label">First Name</label>
                            <input type="text" class="form-control" id="firstname" name="firstname" 
                                value="<?php echo isset($_SESSION["signup_data"]["firstname"]) ? 
                                    htmlspecialchars($_SESSION["signup_data"]["firstname"]) : ''; ?>" required>
                        </div>
                        <div class="col">
                            <label for="lastname" class="form-label">Last Name</label>
                            <input type="text" class="form-control" id="lastname" name="lastname" 
                                value="<?php echo isset($_SESSION["signup_data"]["lastname"]) ? 
                                    htmlspecialchars($_SESSION["signup_data"]["lastname"]) : ''; ?>" required>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" 
                            value="<?php echo isset($_SESSION["signup_data"]["email"]) ? 
                                htmlspecialchars($_SESSION["signup_data"]["email"]) : ''; ?>" required>
                    </div>
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" 
                            value="<?php echo isset($_SESSION["signup_data"]["username"]) ? 
                                htmlspecialchars($_SESSION["signup_data"]["username"]) : ''; ?>" required>
                    </div>
                    <div class="row mb-3">
                        <div class="col">
                            <label for="pwd" class="form-label">Password</label>
                            <input type="password" class="form-control" id="pwd" name="pwd" required>
                            <small class="form-text text-muted">
                                Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.
                            </small>
                        </div>
                        <div class="col">
                            <label for="cpwd" class="form-label">Confirm Password</label>
                            <input type="password" class="form-control" id="cpwd" name="cpwd" required>
                        </div>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary">Sign Up</button>
                    </div>
                </form>
                
                <?php
                // Clear the session data after displaying it
                if (isset($_SESSION["signup_data"])) {
                    unset($_SESSION["signup_data"]);
                }
                ?>
            </div>
        </div>
    </div>
</body>
</html>