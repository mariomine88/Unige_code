<?php
require_once '../../dbh.php';

$token = $_GET['token'] ?? '';
$validToken = false;

if (!empty($token)) {
    try {
        $query = "SELECT id FROM users WHERE activation_token = :token";
        $stmt = $pdo->prepare($query);
        $stmt->execute([':token' => $token]);
        
        if ($user = $stmt->fetch()) {
            // Activate the account
            $updateStmt = $pdo->prepare("UPDATE users SET activation_token = NULL WHERE id = :id");
            $updateStmt->execute([':id' => $user['id']]);
            $validToken = true;
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
                <h3 class="text-center mb-4">Account Activation</h3>
                
                <?php if ($validToken): ?>
                    <div class="alert alert-success" role="alert">
                        Your account has been successfully activated! You can now login.
                    </div>
                    <div class="text-center mt-3">
                        <a href="login.php" class="btn btn-primary">Go to Login</a>
                    </div>
                <?php else: ?>
                    <div class="alert alert-danger" role="alert">
                        Invalid activation token.
                    </div>
                <?php endif; ?>

                <div class="text-center mt-3">
                    <button onclick="window.location.href='../index.php'" class="btn btn-secondary">Return Home</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
