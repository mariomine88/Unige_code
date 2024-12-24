<?php
    $page_title = 'Home'; // Imposta il titolo della pagina
    include 'header.php'; // Include il file <head> con i CSS e i metadati
?>

<body>
    <?php include 'navbar.php'; // Include la navbar ?>
    <div class="container">
        <h1 class="display-4">Benvenuto su NomeSito</h1>
        <p class="lead">Trova i collaboratori perfetti per il tuo progetto!</p>
        <a href="registrazione.php" class="btn btn-primary btn-lg mt-3">Inizia Ora</a>
    </div>

</body>
<?php include 'footer.php'; // Include il footer ?>
</html>