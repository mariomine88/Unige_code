<?php

function generate_random_email() {
    // 5 lower case @ 10 lower case . 3 lower case
    $email = substr(str_shuffle('abcdefghijklmnopqrstuvwxyz'),1,5)
        . '@'
        .substr(str_shuffle('abcdefghijklmnopqrstuvwxyz'),1,10)
        . '.'
        .substr(str_shuffle('abcdefghijklmnopqrstuvwxyz'),1,3);

    return $email;
}

function generate_random_name() {
    // 1 upper case + 8 lower case
    $name = substr(str_shuffle('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 1,1).
        substr(str_shuffle('abcdefghijklmnopqrstuvwxyz'), 1,8);
    return $name;
}

function generate_random_password() {
    $pass = substr(str_shuffle('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@&%$*#'), 1,12);
    return $pass;
}
