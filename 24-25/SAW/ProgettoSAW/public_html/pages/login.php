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
                <div class="d-flex justify-content-start">
                    <button onclick="window.location.href='index.php'" class="btn btn-secondary BackArrow" aria-label="Return Home">
                        <svg xmlns="http://www.w3.org/2000/svg" width="10" height="8" class="bi bi-arrow-left" viewBox="0 0 16 16">
                            <path fill-rule="evenodd" d="M15 8a.5.5 0 0 1-.5.5H2.707l3.147 3.146a.5.5 0 0 1-.708.708l-4-4a.5.5 0 0 1 0-.708l4-4a.5.5 0 1 1 .708.708L2.707 7.5H14.5A.5.5 0 0 1 15 8z"/>
                        </svg>
                    </button>
                </div>
                <h3 class="text-center mb-4">Login</h3>
                
                <?php include '../include/messages.php';
                ?>

                <form action="../BackEnd/login.php" method="post">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username or Email</label>
                        <input type="text" class="form-control" id="username" name="email" aria-label="Username or Email"
                            placeholder="Enter username or email"
                            value="<?php echo isset($_SESSION["login_data"]["username"]) ? 
                                htmlspecialchars($_SESSION["login_data"]["username"]) : ''; ?>" required>
                    </div>
                    <div class="mb-3">
                        <label for="pwd" class="form-label">Password</label>
                        <input type="password" class="form-control" id="pwd" name="pass" aria-label="Password" required>
                    </div>
                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" id="remember" name="remember" aria-label="Remember Me (30 days)">
                        <label class="form-check-label" for="remember">Remember Me (30 days)</label>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary" aria-label="Login">Login</button>
                    </div>
                </form>

                <div class="text-center mt-3">
                <a href="forgot-password.php" class="d-block mb-3" aria-label="Forgot Password">Forgot Password?</a>
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
