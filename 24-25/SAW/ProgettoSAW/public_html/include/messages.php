<?php
if (isset($_SESSION["errors"]) && !empty($_SESSION["errors"])) : ?>
    <div class="alert alert-danger">
        <ul class="mb-0">
            <?php 
            foreach ($_SESSION["errors"] as $error) {
                echo "<li>" . htmlspecialchars($error) . "</li>";
            }
            unset($_SESSION["errors"]);
            ?>
        </ul>
    </div>
<?php endif; ?>

<?php if (isset($_SESSION["success"])) : ?>
    <div class="alert alert-success">
        <?php 
        echo htmlspecialchars($_SESSION["success"]);
        unset($_SESSION["success"]); 
        ?>
    </div>
<?php endif; ?>
