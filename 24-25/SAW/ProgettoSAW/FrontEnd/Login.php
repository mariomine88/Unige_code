<?php
    include 'header.php';
?>
<body>
    <div class="container">
        <div class="login-container">
            <h1 class="login-title">Accedi a Team2Reality</h1>
            <form action="login_process.php" method="POST">
                <!-- Campo Email -->
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input 
                      type="email" 
                      class="form-control" 
                      id="email" 
                      name="email" 
                      placeholder="Inserisci la tua email" 
                      required>
                </div>
                <!-- Campo Password -->
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input 
                      type="password" 
                      class="form-control" 
                      id="password" 
                      name="password" 
                      placeholder="Inserisci la tua password" 
                      required>
                </div>
                <!-- Bottone di Login -->
                <button type="submit" class="btn btn-primary w-100">Accedi</button>
                <!-- Link Registrazione -->
                <div class="text-center mt-3">
                    <small>Non hai un account? <a href="register.php">Registrati qui</a></small>
                </div>
            </form>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script 
      src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js">
    </script>
</body>
</html>