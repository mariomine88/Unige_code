<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $firstname = $_POST['firstname'];
    $lastname = $_POST['lastname'];
    $email = $_POST['email'];
    $username = $_POST['username'];
    $password = $_POST['password'];
    $cpassword = $_POST['cpassword'];


    // Check if any value is null
    if (empty($firstname) || empty($lastname) || empty($email) || empty($username) || empty($password) || empty($cpassword)) {
        echo "All fields are required!";
        header("Location: ../index.php");
        exit();
    }

    // Check if passwords match
    if ($password !== $cpassword) {
        echo "Passwords do not match!";
        header("Location: ../index.php");
        exit();
    }

    // Hash the password
    $hashedPassword = password_hash($password, PASSWORD_BCRYPT);

    // Here you can add code to insert the data into a database
    // For example:
    try {
        require_once 'dbh.php';
        $query = "INSERT INTO users (firstname, lastname, email, username, password) VALUES 
        (:firstname, :lastname, :email, :username, :password)";

        $stmt = $pdo->prepare($query);

        $stmt->bindParam(':firstname', $firstname);
        $stmt->bindParam(':lastname', $lastname);
        $stmt->bindParam(':email', $email);
        $stmt->bindParam(':username', $username);
        $stmt->bindParam(':password', $hashedPassword);

        $stmt->execute();

        $pdo = null;
        $stmt = null;


        echo "Signup successful!";
        header("Location: ../index.php");
        die();
    } catch (PDOException $e) {
        die("Error: " . $e->getMessage());
    }
    
}else{
    echo "You are not allowed to access this page!";
    //header("Location: ../index.php");
}