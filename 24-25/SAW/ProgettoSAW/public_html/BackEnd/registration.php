<?php
if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: ../pages/index.php");
    die();
}

require_once 'config_session.php';
require_once 'check_imput.php';


function sendActivationEmail(&$email,&$activation_token) {
    try {
        require_once '../../mail-init.php'; 
        $activation_token = bin2hex(random_bytes(32));
        $activationLink = "https://saw.dibris.unige.it/~s5577783/pages/activate.php?token=" . $activation_token;
        
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
        return true;
    } catch (Exception $e) {
        $activation_token = null;
        if (strpos($e->getMessage(), 'invalid address') !== false) {
            $_SESSION["signup_errors"] = "Email address doesn't exist";
            header("Location: ../FrontEnd/signup.php");
            exit();
        } else {
            header("Location: ../FrontEnd/500.php");
            exit();
        }
    }
}


$firstname = trim($_POST['firstname'] ?? '');
$lastname = trim($_POST['lastname'] ?? '');
$email = trim($_POST['email'] ?? '');
$username = trim($_POST['username'] ?? '');
$pwd = trim($_POST['pass'] ?? '');
$cpwd = trim($_POST['cpwd'] ?? '');

//for test uncoment
//$username = "test";
//$cpwd = $pwd;

// Validate basic fields
$errors = validateBasicFields($firstname, $lastname, $email, $username);

// Validate password
$errors = array_merge($errors, validatePassword($pwd, $cpwd));

require_once '../../check_email.php';

if ($response === "invalid") {
    $errors[] = "Please provide a valid email address";
}

try {
    require_once '../../dbh.php';
    // Check for existing user
    $errors = array_merge($errors, checkExistingUser($pdo, $email, $username));

    if (!empty($errors)) {
        $_SESSION["errors"] = $errors;
        $_SESSION["data"] = [
            "firstname" => $firstname,
            "lastname" => $lastname,
            "email" => $email,
            "username" => $username
        ];
        header("Location: ../pages/signup.php");
        die();
    }

    // Handle activation token
    $activation_token = null;

    //for test coment
    sendActivationEmail($email,$activation_token);

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
    ':activation_token' => $activation_token
    ]);

    $stmt = null;
    $pdo = null;

    // Clear session and set success
    unset($_SESSION["errors"], $_SESSION["data"]);
    $_SESSION["success"] = "Account created successfully! Please check your email to activate your account.";
    
    header("Location: ../pages/signup.php");
    die();

} catch (PDOException $e) {
    header("Location: ../pages/errors_pages/500.php");
    die();
}
