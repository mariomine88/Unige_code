<?php
require_once 'config_session.php';
require_once 'dbh.php';
require_once 'check_imput.php';
require_once 'mail-init.php'; 

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $firstname = trim($_POST['firstname'] ?? '');
    $lastname = trim($_POST['lastname'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $username = trim($_POST['username'] ?? '');
    $pwd = trim($_POST['pwd'] ?? '');
    $cpwd = trim($_POST['cpwd'] ?? '');

    // Validate basic fields
    $errors = validateBasicFields($firstname, $lastname, $email, $username);
    
    // Validate password
    $errors = array_merge($errors, validatePassword($pwd, $cpwd));

    try {
        // Check for existing user
        $errors = array_merge($errors, checkExistingUser($pdo, $email, $username));

        if (!empty($errors)) {
            $_SESSION["signup_errors"] = $errors;
            $_SESSION["signup_data"] = [
                "firstname" => $firstname,
                "lastname" => $lastname,
                "email" => $email,
                "username" => $username
            ];
            header("Location: ../pages/signup.php");
            die();
        }

        // Generate activation token
        $activationToken = urlencode(bin2hex(random_bytes(32)));
        

        // Send activation email
        $activationLink = "https://saw.dibris.unige.it/~s5577783/pages/activate.php?token=" . $activationToken;
        
        try {
            $mail->setFrom('saws5577783donotreply@gmail.com', 'Account Activation');
            $mail->addAddress($email);
            $mail->isHTML(true);
            $mail->Subject = 'Activate Your Account';
            $mail->Body = "
                <h2>Account Activation</h2>
                <p>Thank you for registering! Please activate your account.</p>
                <p>Please click the link below to activate your account:</p>
                <p><a href='{$activationLink}'>Activate Account</a></p>
                <p>If you didn't create this account, please ignore this email.</p>
            ";
            $mail->AltBody = "Activate your account: {$activationLink}";
            $mail->send();
            
        } catch (Exception $e) {
            if (strpos($e->getMessage(), 'invalid address') !== false) {
                $_SESSION["signup_errors"] = "Email address doesn't exist";
                header("Location: ../FrontEnd/signup.php");
                exit();
            } else {
                header("Location: ../FrontEnd/500.php");
                exit();
            }
        }

        $hashedPwd = password_hash($pwd, PASSWORD_BCRYPT, ["cost" => 12]);

        $query = "INSERT INTO users (firstname, lastname, email, username, password, activation_token) 
        VALUES (:firstname, :lastname, :email, :username, :password, :activation_token)";
        $stmt = $pdo->prepare($query);

        $stmt->execute([
        ':firstname' => $firstname,
        ':lastname' => $lastname,
        ':email' => $email,
        ':username' => $username,
        ':password' => $hashedPwd,
        ':activation_token' => $activationToken
        ]);

        $stmt = null;
        $pdo = null;

        // Clear session and set success
        unset($_SESSION["signup_errors"], $_SESSION["signup_data"]);
        $_SESSION["signup_success"] = "Account created successfully! Please check your email to activate your account.";
        
        header("Location: ../pages/signup.php");
        die();

    } catch (PDOException $e) {
        header("Location: ../pages/errors_pages/500.php");
        die();
    }
}