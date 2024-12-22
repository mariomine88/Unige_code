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
                    if (isset($_SESSION["signup_success"])) {
                        echo '<div class="alert alert-success alert-dismissible fade show" role="alert">
                                ' . $_SESSION["signup_success"] . '
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                              </div>';
                        unset($_SESSION["signup_success"]);
                    }
                ?>
                <form action="../include/loginhandler.php" method="post">
                    <div class="mb-3">
                        <input type="text" class="form-control" name="username" placeholder="Username">
                    </div>
                    <div class="mb-3">
                        <input type="password" class="form-control" name="password" placeholder="Password">
                    </div>
                    <div class="text-center">
                        <button type="submit" name="submit" class="btn btn-primary">Login</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
