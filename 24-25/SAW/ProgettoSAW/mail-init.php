<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require 'PHPMailer/src/Exception.php';
require 'PHPMailer/src/PHPMailer.php';
require 'PHPMailer/src/SMTP.php';

$config = json_decode(file_get_contents(__DIR__ . '/config.json'), true);
$smtp = $config['smtp'];

$mail = new PHPMailer(true);

$mail->isSMTP();
$mail->Host = $smtp['host'];
$mail->SMTPSecure = "ssl";
$mail->Port = $smtp['port'];

$mail->SMTPAuth = true;
$mail->Username = $smtp['username'];
$mail->Password = $smtp['password'];