<?php 
require_once '../backend/config_session.php';

// Redirect if not logged in or no profile data
if (!isset($_SESSION["user_id"]) || !isset($_SESSION["profile_data"])) {
    header("Location: ../index.php");
    die();
}

$user = $_SESSION["profile_data"];
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
    <title>Profile - My Website</title>
</head>
<body>
    <?php include '../include/navbar.php'; ?>

    <div class="container mt-5">
        <h2>Edit Profile</h2>
        
        <?php if (isset($_SESSION["update_errors"])) : ?>
            <div class="alert alert-danger">
                <ul class="mb-0">
                    <?php 
                    foreach ($_SESSION["update_errors"] as $error) {
                        echo "<li>" . htmlspecialchars($error) . "</li>";
                    }
                    unset($_SESSION["update_errors"]);
                    ?>
                </ul>
            </div>
        <?php endif; ?>
        
        <?php if (isset($_SESSION["profile_updated"])) : ?>
            <div class="alert alert-success">
                Profile updated successfully!
            </div>
            <?php unset($_SESSION["profile_updated"]); ?>
        <?php endif; ?>

        <form action="../backend/update_profile.php" method="post" class="mt-4">
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
    </div>
</body>
</html>
