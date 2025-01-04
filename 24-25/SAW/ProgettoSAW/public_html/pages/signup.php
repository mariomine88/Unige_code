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
                    <button onclick="window.location.href='index.php'" class="btn btn-secondary" aria-label="Return Home">
                        <svg xmlns="http://www.w3.org/2000/svg" width="10" height="8" class="bi bi-arrow-left" viewBox="0 0 16 16">
                            <path fill-rule="evenodd" d="M15 8a.5.5 0 0 1-.5.5H2.707l3.147 3.146a.5.5 0 0 1-.708.708l-4-4a.5.5 0 0 1 0-.708l4-4a.5.5 0 1 1 .708.708L2.707 7.5H14.5A.5.5 0 0 1 15 8z"/>
                        </svg>
                    </button>
                </div>
                <h3 class="text-center mb-4">Sign Up</h3>
                
                <?php include '../include/messages.php'; ?>

                <form action="../BackEnd/registration.php" method="post">
                    <div class="row mb-3">
                        <div class="col">
                            <label for="firstname" class="form-label">First Name</label>
                            <input type="text" class="form-control" id="firstname" name="firstname" aria-label="First Name"
                                value="<?php echo isset($_SESSION["data"]["firstname"]) ? 
                                    htmlspecialchars($_SESSION["data"]["firstname"]) : ''; ?>" required>
                        </div>
                        <div class="col">
                            <label for="lastname" class="form-label">Last Name</label>
                            <input type="text" class="form-control" id="lastname" name="lastname" aria-label="Last Name"
                                value="<?php echo isset($_SESSION["data"]["lastname"]) ? 
                                    htmlspecialchars($_SESSION["data"]["lastname"]) : ''; ?>" required>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" aria-label="Email"
                            value="<?php echo isset($_SESSION["data"]["email"]) ? 
                                htmlspecialchars($_SESSION["data"]["email"]) : ''; ?>" required>
                    </div>
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" aria-label="Username"
                            value="<?php echo isset($_SESSION["data"]["username"]) ? 
                                htmlspecialchars($_SESSION["data"]["username"]) : ''; ?>" required>
                    </div>
                    <div class="row mb-3">
                        <div class="col">
                            <label for="pwd" class="form-label">Password</label>
                            <input type="password" class="form-control" id="pwd" name="pass" aria-label="Password" required minlength="8">
                        </div>
                        <div class="col">
                            <label for="cpwd" class="form-label">Confirm Password</label>
                            <input type="password" class="form-control" id="cpwd" name="cpwd" aria-label="Confirm Password" required minlength="8">
                        </div>
                        <small class="form-text text-muted">
                                Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.
                        </small>
                    </div>
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" name="tos_agree" id="tos_agree" aria-label="Agree to Terms of Service" required>
                        <label class="form-check-label" for="tos_agree">
                         I read and agree the
                        <a href="TermsOfService.html" target="_Parent">Terms of Service</a>
                        </label>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary" aria-label="Sign Up">Sign Up</button>
                    </div>
                </form>
                
                <div class="text-center mt-3">
                    <p><strong>Already have an account?</strong>
                    <button onclick="window.location.href='login.php'" class="btn btn-secondary btn-sm ms-2" aria-label="Log In">Log In</button></p>
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