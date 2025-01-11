<?php 
require_once '../BackEnd/config_session.php';

if (!isset($_SESSION["user_id"])) {
    header("Location: ../index.php");
    die();
}

// Use the new data session variable
$user = $_SESSION["data"];
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
</head>
<body>
    <?php include '../include/navbar.php'; ?>

    <div class="container mt-5 mb-5">
        <h2>Edit Profile</h2>
        
        <?php include '../include/messages.php'; ?>

        <form action="../BackEnd/update_profile.php" method="post" class="mt-4">
            <div class="mb-3">
                <label for="firstname" class="form-label">First Name</label>
                <input type="text" class="form-control" id="firstname" name="firstname" 
                       value="<?php echo htmlspecialchars($user['firstname']); ?>" required>
            </div>
            <div class="mb-3">
                <label for="lastname" class="form-label">Last Name</label>
                <input type="text" class="form-control" id="lastname" name="lastname" 
                       value="<?php echo htmlspecialchars($user['lastname']); ?>" required>
            </div>
            <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" class="form-control" id="username" name="username" 
                       value="<?php echo htmlspecialchars($user['username']); ?>" required>
            </div>
            <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" name="email" 
                       value="<?php echo htmlspecialchars($user['email']); ?>" required>
            </div>
            <hr>
            <h4>Change Password</h4>
            <div class="mb-3">
                <label for="old_password" class="form-label">Current Password</label>
                <input type="password" class="form-control" id="old_password" name="old_password">
            </div>
            <div class="mb-3">
                <label for="new_password" class="form-label">New Password</label>
                <input type="password" class="form-control" id="new_password" name="new_password">
                <small class="form-text text-muted">Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.</small>
            </div>
            <div class="mb-3">
                <label for="confirm_password" class="form-label">Confirm New Password</label>
                <input type="password" class="form-control" id="confirm_password" name="confirm_password">
            </div>
            <button type="submit" class="btn btn-primary">Update Profile</button>
        </form>
        <!-- Add delete account section -->
        <div class="mt-5 border-top pt-4">
            <h4 class="text-danger">Delete Account</h4>
            <p>Warning: This action cannot be undone. All your data will be permanently deleted.</p>
            <form action="../BackEnd/delete_account.php" method="post" onsubmit="return confirmDelete();">
                <button type="submit" class="btn btn-danger">Delete Account</button>
            </form>
        </div>
    </div>

    <div class="mb-5"></div>

    <script>
    function confirmDelete() {
        return confirm("Are you sure you want to delete your account? This action cannot be undone.");
    }
    </script>
</body>
</html>
