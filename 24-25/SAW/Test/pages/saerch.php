<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $usernamesaerch = $_POST['usernamesaerch'];

    // Check if any value is null
    if (empty($usernamesaerch)) {
        echo "All fields are required!";
    } else {
        try {
            require_once 'include/dbh.php';

            $query = "SELECT username FROM users WHERE username LIKE :usernamesaerch";
            $stmt = $pdo->prepare($query);
            $usernamesaerch = "%" . $usernamesaerch . "%"; // Add wildcards for partial match
            $stmt->bindParam(':usernamesaerch', $usernamesaerch);
            $stmt->execute();

            $result = $stmt->fetchAll(PDO::FETCH_ASSOC);

            $pdo = null;
            $stmt = null;
        } catch (PDOException $e) {
            die("Error: " . $e->getMessage());
        }
    }
} else {
    $result = [];
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>

    <H3>Saerch user</H3>

    <form action="saerch.php" method="post">
        <input type="text" name="usernamesaerch" placeholder="saerch user">
        <button type="submit" name="submit">Saerch</button>
    </form>

    <div>
        <?php
        if (!empty($result)) {
            foreach ($result as $row) {
                echo htmlspecialchars($row['username']) . "<br>";
            }
        } else {
            echo "No user found!";
        }
        ?>
    </div>
    
</body>
</html>