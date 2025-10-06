<?php

// Read config file
$config = json_decode(file_get_contents(__DIR__ . '/config.json'), true);
$api_key = $config['abstractapi']['email_validation_key'];

$url = "https://emailvalidation.abstractapi.com/v1/?api_key=" . $api_key . "&email=" . urlencode($email);

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);
$response;

// Check if email is valid according to AbstractAPI
if ($result['deliverability'] === "UNDELIVERABLE" || 
    $result['is_valid_format']['value'] === false) {
    $response = "invalid";
} else {
    $response = "valid";
}

