<?php
require_once '../BackEnd/config_session.php';
require_once '../BackEnd/dbh.php';

$token = $_GET['token'] ?? '';
$validToken = false;
$email = '';

if (!empty($token)) {
    try {
        $query = "SELECT email FROM password_resets 
                 WHERE token = :token 
                 AND expires_at > NOW()";
        $stmt = $pdo->prepare($query);
        $stmt->execute([':token' => $token]);
        $result = $stmt->fetch();
        
        if ($result) {
            $validToken = true;
            $email = $result['email'];
        }
    } catch (PDOException $e) {
        header("Location: errors_pages/500.php");
        die();
    }
}
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

                if (!$validToken) {
                    echo '<div class="alert alert-danger" role="alert">
                            Invalid or expired reset link. Please request a new password reset.
                          </div>';
                    echo '<div class="text-center mt-3">
                            <a href="forgot-password.php" class="btn btn-primary">Request New Reset Link</a>
                          </div>';
                } else {
                ?>
                    <form action="../BackEnd/reset-password-handler.php" method="post">
                        <input type="hidden" name="token" value="<?php echo htmlspecialchars($token); ?>">
                        <input type="hidden" name="email" value="<?php echo htmlspecialchars($email); ?>">
                        
                        <div class="mb-3">
                            <label for="pwd" class="form-label">New Password</label>
                            <input type="password" class="form-control" id="pwd" name="pwd" 
                                   required minlength="8">
                        </div>
                        <div class="mb-3">
                            <label for="cpwd" class="form-label">Confirm New Password</label>
                            <input type="password" class="form-control" id="cpwd" name="cpwd" 
                                   required minlength="8">
                        </div>
                        <div class="text-center">
                            <button type="submit" class="btn btn-primary">Reset Password</button>
                        </div>
                    </form>
                <?php } ?>

                <div class="text-center mt-3">
                <button onclick="window.location.href='../index.php'" class="btn btn-secondary">Return Home</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
