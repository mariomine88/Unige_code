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
                <h3 class="text-center mb-4">Reset Password</h3>
                
                <?php
                if (isset($_SESSION["reset_errors"]) && !empty($_SESSION["reset_errors"])) {
                    foreach ($_SESSION["reset_errors"] as $error) {
                        echo '<div class="alert alert-danger" role="alert">' . htmlspecialchars($error) . '</div>';
                    }
                    unset($_SESSION["reset_errors"]);
                }

                if (isset($_SESSION["reset_success"])) {
                    echo '<div class="alert alert-success" role="alert">' . htmlspecialchars($_SESSION["reset_success"]) . '</div>';
                    unset($_SESSION["reset_success"]);
                }
                ?>

                <form action="../BackEnd/forgot-password-handler.php" method="post">
                    <div class="mb-3">
                        <label for="email" class="form-label">Email Address</label>
                        <input type="email" class="form-control" id="email" name="email" 
                            placeholder="Enter your email address"
                            value="<?php echo isset($_SESSION["reset_data"]["email"]) ? 
                                htmlspecialchars($_SESSION["reset_data"]["email"]) : ''; ?>" required>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary">Send Reset Link</button>
                    </div>
                </form>

                <div class="text-center mt-3">
                    <button onclick="window.location.href='login.php'" class="btn btn-secondary">Back to Login</button>
                </div>

                <?php
                if (isset($_SESSION["reset_data"])) {
                    unset($_SESSION["reset_data"]);
                }
                ?>
            </div>
        </div>
    </div>
</body>
</html>
