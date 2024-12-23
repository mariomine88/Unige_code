<?php 
    $page_title = 'Login';

    include 'header.php'; 
?>
<body>
    <div class="container">
        <form class="w-50" action="login_process.php" method="POST">
            <h1 class="mb-4 text-center">Accedi</h1>
            <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" name="email" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <div class="mb-3 text-center">
                <a href="#">Password dimenticata?</a>
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
            <div class="mt-3 text-center">
                <p>Non hai un account? <a href="registrazione.php">Registrati</a></p>
            </div>
        </form>
    </div>

    <?php include 'footer.php'; ?>
</body>
</html>
