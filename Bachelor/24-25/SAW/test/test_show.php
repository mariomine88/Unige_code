<?php
function show_logged_user($baseurl) {

    $ch = curl_init();
    $url = "$baseurl/show_profile.php";

    $cookieFile = "cookies";
    if(!file_exists($cookieFile)) {
        $fh = fopen($cookieFile, "w");
        fwrite($fh, "");
        fclose($fh);
    }

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

    $headers = array();
    $headers[] = 'Content-Type: application/x-www-form-urlencoded';
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_COOKIEFILE, $cookieFile); // Cookie aware
    curl_setopt($ch, CURLOPT_COOKIEJAR, $cookieFile); // Cookie aware
    $result = curl_exec($ch);

    /* Delete comment below to see what is returned */
    echo $result;

    if (curl_errno($ch)) {
        echo 'Error:' . curl_error($ch);
    }
    curl_close($ch);
    return $result;
} 

function check_correct_user($email, $first_name, $last_name, $show_page) {
	return strpos($show_page, $email) && strpos($show_page, $first_name) && strpos($show_page, $last_name); 
}
