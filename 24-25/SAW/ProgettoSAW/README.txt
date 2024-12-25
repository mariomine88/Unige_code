https://saw.dibris.unige.it/~s5577783/pages/index.php
https://saw.dibris.unige.it/phpmyadmin


files structure

pages contain the pages has a folder for the errors pages
include for thhe include in the pages
js for js
css for css
image for image
BackEnd for the pure php files mosty for the sql querry

sql

the useer TABLE

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);


CREATE TABLE auth_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    selector CHAR(32) NOT NULL UNIQUE,
    token CHAR(64) NOT NULL,
    user_id INT NOT NULL,
    expires DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
