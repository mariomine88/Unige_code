<?php require_once '../BackEnd/config_session.php'; ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <?php include '../include/header.php'; ?>
    <style>
        .hero-section {
            padding: 100px 0;
            text-align: center;
            background-color: #f8f9fa;
        }
        .about-section {
            padding: 50px 0;
        }
    </style>
</head>
<body>
    <?php include '../include/navbar.php'; ?>

    <div class="hero-section">
        <div class="container">
            <h1 class="display-4">About Our Project</h1>
            <p class="lead">Learn more about our mission and support our development</p>
        </div>
    </div>

    <div class="about-section">
        <div class="container">
            <div class="row">
                <div class="col-md-8 mx-auto text-center">
                    <h2>Our Mission</h2>
                    <p class="lead mb-5">We're building a community-driven platform where people can connect, share ideas, and engage in meaningful conversations.</p>
                    
                    <h3>Support Our Development</h3>
                    <p class="mb-4">Help us improve and maintain this platform by contributing or supporting us.</p>
                    
                    <div class="d-flex justify-content-center gap-3">
                        <a href="https://github.com/mariomine88/Unige_code/tree/main/24-25/SAW/ProgettoSAW" class="btn btn-outline-dark" target="_blank">
                            <i class="fa fa-github"></i> Github
                        </a>
                        <a href="https://paypal.me/eugeniovassallo?country.x=IT&locale.x=it_IT" class="btn btn-outline-primary" target="_blank">
                            <i class="fa fa-paypal"></i> Support Us
                        </a>
                    </div>
                    <div class="text-center my-4">
                        <a href="TermsOfService.html" class="text-muted" style="text-decoration: underline;">Terms of Service</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
