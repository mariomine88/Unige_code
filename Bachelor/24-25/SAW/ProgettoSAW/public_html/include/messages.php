<?php
if (isset($_SESSION["errors"]) && !empty($_SESSION["errors"])) : ?>
    <div class="alert alert-danger">
        <ul class="mb-0">
            <?php 
            if (is_array($_SESSION["errors"])) {
                foreach ($_SESSION["errors"] as $error) {
                    echo "<li>" . htmlspecialchars($error) . "</li>";
                }
            } else {
                echo "<li>" . htmlspecialchars($_SESSION["errors"]) . "</li>";
            }
            unset($_SESSION["errors"]);
            ?>
        </ul>
    </div>
<?php endif; ?>

<?php if (isset($_SESSION["success"])) : ?>
    <div class="alert alert-success">
        <?php 
        if (is_array($_SESSION["success"])) {
            foreach ($_SESSION["success"] as $message) {
                echo htmlspecialchars($message) . "<br>";
            }
        } else {
            echo htmlspecialchars($_SESSION["success"]);
        }
        unset($_SESSION["success"]); 
        ?>
    </div>
<?php endif; ?>
