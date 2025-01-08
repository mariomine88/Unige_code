https://saw.dibris.unige.it/~s5577783/pages/index.php
https://saw.dibris.unige.it/phpmyadmin


files structure

pages contain the pages has a folder for the errors pages
include for thhe include in the pages
js for js
css for css
image for image
BackEnd for the pure php files mosty for the sql querry

the dbh.php and mail-init are saved outside the public folder 
and use the credenzias saved in config.json( that is nn in this repo for obvius resons)

the sql table are in the sql file

---------------------------------TEST-------------------------------------------
nota: 
i test automatici di base non vengono passati, per passarli bisogna disattivare
alcune funzioni aggiuntive nei file:

!registration.php -> uncomment rows: 53,54,65 and comment rows: 64,92
(questo disabilità la conferma password, l'username nei test non viene fornito quindi
lo impostiamo $username = $firstname e togliamo la verifica via mail con token di attivazione)

!show_profile.php -> uncomment rows: 26,27,28 
(questo perchè noi passiamo i dati via sessione ma i test leggono l'html)

!update_profile.php -> row: 18 set $test = TRUE
(perchè l'imput dei test è più corto di quello nella nostra implementazione)
--------------------------------------------------------------------------------