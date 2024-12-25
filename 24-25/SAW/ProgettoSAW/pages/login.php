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
                <h3 class="text-center mb-4">Login</h3>
                
                <?php
                if (isset($_SESSION["login_errors"]) && !empty($_SESSION["login_errors"])) {
                    foreach ($_SESSION["login_errors"] as $error) {
                        echo '<div class="alert alert-danger" role="alert">' . htmlspecialchars($error) . '</div>';
                    }
                    unset($_SESSION["login_errors"]);
                }

                if (isset($_SESSION["signup_success"])) {
                    echo '<div class="alert alert-success" role="alert">' . htmlspecialchars($_SESSION["signup_success"]) . '</div>';
                    unset($_SESSION["signup_success"]);
                }
                ?>

                <form action="../BackEnd/loginhandler.php" method="post">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username or Email</label>
                        <input type="text" class="form-control" id="username" name="username" 
                            placeholder="Enter username or email"
                            value="<?php echo isset($_SESSION["login_data"]["username"]) ? 
                                htmlspecialchars($_SESSION["login_data"]["username"]) : ''; ?>" required>
                    </div>
                    <div class="mb-3">
                        <label for="pwd" class="form-label">Password</label>
                        <input type="password" class="form-control" id="pwd" name="pwd" required>
                    </div>
                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" id="remember" name="remember">
                        <label class="form-check-label" for="remember">Remember Me (30 days)</label>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary">Login</button>
                    </div>
                </form>

                <div class="text-center mt-3">
                    <button onclick="window.location.href='../index.php'" class="btn btn-secondary">Return Home</button>
                </div>

                <?php
                if (isset($_SESSION["login_data"])) {
                    unset($_SESSION["login_data"]);
                }
                ?>
            </div>
        </div>
    </div>
</body>
</html>
