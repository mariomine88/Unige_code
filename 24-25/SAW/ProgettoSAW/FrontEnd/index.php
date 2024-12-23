<?php
    $page_title = 'Home';
    include 'header.php';

    include 'navbar.php';   
?>
<body>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>Trova i collaboratori perfetti per il tuo progetto</h1>
            <p>Team2Reality ti aiuta a trasformare la tua idea in un progetto concreto, connettendoti con professionisti e appassionati.</p>
            <a href="registrazione.php" class="btn btn-primary btn-lg">Inizia Ora</a>
        </div>
    </section>

    <!-- Sezione caratteristiche/valori -->
    <section class="section-features">
        <div class="container">
            <h2>Perché scegliere Team2Reality?</h2>
            <div class="row">
                <!-- Feature 1 -->
                <div class="col-md-4 mb-4 text-center">
                    <div class="card shadow-sm">
                        <div class="card-body">
                            <h5 class="card-title fw-bold">Crea e Condividi</h5>
                            <p class="card-text">Pubblica la tua idea in pochi clic e rendila visibile a tutta la community.</p>
                        </div>
                    </div>
                </div>
                <!-- Feature 2 -->
                <div class="col-md-4 mb-4 text-center">
                    <div class="card shadow-sm">
                        <div class="card-body">
                            <h5 class="card-title fw-bold">Trova Talenti</h5>
                            <p class="card-text">Ricerca membri con competenze specifiche, filtra e scegli i collaboratori ideali.</p>
                        </div>
                    </div>
                </div>
                <!-- Feature 3 -->
                <div class="col-md-4 mb-4 text-center">
                    <div class="card shadow-sm">
                        <div class="card-body">
                            <h5 class="card-title fw-bold">Costruisci la Tua Realtà</h5>
                            <p class="card-text">Trasforma un’idea in un team, un team in un prototipo, un prototipo in un prodotto reale.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

<?php
    include 'footer.php';
?>

