/*
OPERAZIONI E INFORMAZIONI PRELIMINARI

Dopo esservi posizionati sullo schema corretto con il comando set search_path to 'information_schema',
 scrivere una interrogazione SQL per recuperare tutte le tuple contenute 
 nella tabella catalogo table_privileges, analizzarne lo schema e l'istanza. 
 Cercate di comprendere il significato degli attributi (escluso l'attributo with_hierarchy).
*/

SET search_path TO 'information_schema';
SELECT * FROM table_privileges;

/*
1.Scrivere una o più interrogazioni  per recuperare dal catalogo table_privileges
le informazioni relative ai privilegi delle tabelle contenute nello schema unicorsi.
*/

SELECT * 
FROM table_privileges 
WHERE table_schema = 'unicorsi';

/*
Creare l'utente yoda (con password yoda) e l'utente luke (con password luke).
Usare il comando CREATE USER nome PASSWORD 'password')
 e verificare, nel menu di navigazione a sinistra, l'avvenuta creazione degli utenti 
 (sotto la voce Login/Group Roles associata al vostro database)
[in Postgres ogni utente è visto come un ruolo che ha la possibilità di connettersi al DBMS,
 inoltre l'utente amministratore, postgres, può rivestire tutti i ruoli, quindi tutti gli utenti, creati.]
*/


CREATE USER yoda PASSWORD 'yoda';
CREATE USER luke PASSWORD 'luke';

--fare logout e poi login con l'utente yoda
/*
3.Siete collegati come utente yoda. Provate ad eseguire la query per recuperare
le informazioni di tutti gli studenti. Riuscite ad eseguire l'operazione? 
Quale risultato viene restituito? Perché?
*/

SELECT * FROM studenti;

--ERROR:  relation "studenti" does not exist
--errore perchè l'utente yoda non ha i privilegi select
/*
4. Siete collegati come utente yoda. Scrivere una o più interrogazioni
per recuperare dal catalogo table_privileges le informazioni relative 
ai privilegi dell'utente yoda e cercate conferma alla motivazione proposta al punto.
*/

SET search_path TO 'information_schema';

SELECT * 
FROM table_privileges 
WHERE grantee = 'yoda';

--restituisce 0 righe, perchè l'utente yoda non ha privilegi
/*
5.Siete collegati come utente postgres.
Concedere a yoda per prima cosa il privilegio di utilizzare lo schema unicorsi (con grant option) mediante il comando:
GRANT USAGE ON SCHEMA unicorsi TO yoda WITH GRANT OPTION.
Questo comando permetterà all'utente yoda di utilizzare le tabelle presenti nello schema secondo i privilegi che gli verranno concessi.
A questo punto, concedete a yoda il privilegio di lettura su tutte le tabelle tranne pianidistudio.
Solo il privilegio di lettura concesso sulle tabelle corsidilaurea e corsi deve essere delegabile.
*/

GRANT USAGE ON SCHEMA unicorsi TO yoda WITH GRANT OPTION

GRANT SELECT ON ALL TABLES IN SCHEMA unicorsi TO yoda;
REVOKE SELECT ON TABLE pianidistudio FROM yoda;
GRANT SELECT ON TABLE corsidilaurea TO yoda WITH GRANT OPTION;
GRANT SELECT ON TABLE corsi TO yoda WITH GRANT OPTION;
/*
6.Siete collegati come utente postgres. Senza disconnettervi, 
cambiate il vostro ruolo/utente in yoda (ricordate che in PostgreSQL 
ogni utente è anche un ruolo e l'utente postgres può rivestire ogni ruolo) 
con il comando SET ROLE nomeutente.
*/

SET ROLE yoda;
/*
7.Adesso siete collegati come utente postgres ma agite come utente yoda.
Eseguite di nuovo la query per recuperare le informazioni degli studenti.
Riuscite ad eseguire l'operazione? Quale risultato viene restituito? Perché?
*/

SELECT * FROM studenti;

--restitusce tutte le rige della tabella studenti

SELECT * FROM pianidistudio;

--permission denied for table pianidistudio 

/*
8.Siete collegati come utente postgres ma agite come utente  yoda. 
Scrivere una o più interrogazioni per recuperare dal catalogo table_privileges 
le informazioni relative ai privilegi dell'utente yoda e cercate conferma alla 
motivazione proposta al punto
*/

SET search_path TO 'information_schema';
SELECT * FROM table_privileges WHERE grantee = 'yoda';
/*
risultato:

"grantor"	"grantee"	"table_catalog"	"table_schema"	"table_name"	"privilege_type"	"is_grantable"	"with_hierarchy"
"postgres"	"yoda"	"postgres"	"unicorsi"	"corsidilaurea"	"SELECT"	"YES"	"YES"
"postgres"	"yoda"	"postgres"	"unicorsi"	"corsi"	"SELECT"	"YES"	"YES"
"postgres"	"yoda"	"postgres"	"unicorsi"	"professori"	"SELECT"	"NO"	"YES"
"postgres"	"yoda"	"postgres"	"unicorsi"	"studenti"	"SELECT"	"NO"	"YES"
"postgres"	"yoda"	"postgres"	"unicorsi"	"esami"	"SELECT"	"NO"	"YES"

ci sono 6 nuove righe, che indicano che l'utente yoda ha i privilegi di select 
su tutte le tabelle tranne pianidistudio.
Inoltre select su corsidilaurea e corsi hanno "is_grantable" quindi si posono delegare 
*/
/*
9.Siete collegati come utente postgres ma agite come utente yoda. 
Concedere a luke il privilegio di lettura su studenti, in modalità non delegabile.
Riuscite ad eseguire l'operazione? Quale risultato viene restituito? Perché?
*/

SET search_path TO 'unicorsi';
GRANT SELECT ON TABLE studenti TO luke;

--ERROR:no privileges were granted for "studenti"

y--oda non può concedere select su studenti a luke perchè non ha "is_grantable" = YES
/*
10.Siete collegati come utente postgres ma agite come utente  yoda.
Ora concedere a luke il privilegio di lettura su corsi. Riuscite ad eseguire l'operazione?
Quale risultato viene restituito? Perché?
*/

GRANT SELECT ON TABLE corsi TO luke;

--yoda può concedere select su corsi a luke perchè ha "is_grantable" = YES
/*
11.Siete collegati come utente postgres ma agite come utente  yoda.
Senza disconnettervi, cambiate il vostro ruolo nuovamente
in postgres con il comando SET ROLE nomeutente.
*/

SET ROLE postgres;
/*
12.Siete collegati come utente postgres. 
Revocare all'utente yoda  il privilegio di lettura sulla tabella corsi,
con modalità RESTRICT. Riuscite ad eseguire l'operazione? 
Quale risultato viene restituito? Perché?
*/

REVOKE SELECT ON TABLE corsi FROM yoda RESTRICT;

--errore: dependent privileges exist
--HINT:  Use CASCADE to revoke them too. 
/*
non posso farlo perche essistono privilegi che ne dipendono,cioè 
quello che yoda ha concesso a luke
per rimuovere i privilegi devo usare CASCADE
*/
/*
13.ete collegati come utente postgres. Scrivere una o più interrogazioni 
sul catalogo table_privileges per trovare la conferma alla motivazione data al punto 
*/

SET search_path TO 'information_schema';
SELECT * FROM table_privileges WHERE grantee = 'luke';

--"grantor"	"grantee"	"table_catalog"	"table_schema"	"table_name"	"privilege_type"	"is_grantable"	"with_hierarchy"
--"yoda"	"luke"	"postgres"	"unicorsi"	"corsi"	"SELECT"	"NO"	"YES"
/*
14.Siete collegati come utente postgres. 
Revocare a yoda  il privilegio di lettura sulla tabella corsi,
con modalità CASCADE. Riuscite ad eseguire l'operazione? 
Quale risultato viene restituito? Perché?
*/

REVOKE SELECT ON TABLE corsi FROM yoda cascade;

--si riesco a eseguire l'operazione, perchè ho usato CASCADE
/*
15.Siete collegati come utente postgres.
Scrivere una o più interrogazioni sul catalogo table_privileges 
per trovare la conferma alla motivazione data al punto 
*/

SET search_path TO 'information_schema';
SELECT * FROM table_privileges WHERE grantee = 'yoda';

--ritona 4 righe, che indicano che l'utente yoda non ha più i privilegi di select su corsi
--e se sostituisco yoda con luke, non ci sono più righe
/*
16.Siete collegati come utente postgres. Create i ruoli jedi e maestroJedi 
con il comando CREATE ROLE nomeruolo. Utilizzando la documentazione  di PostgreSQL,
 individuare ed eseguire i seguenti comandi:
revocate il privilegio di SELECT su corsi e studenti a joda e luke;
definire il ruolo maestroJedi come ruolo padre rispetto al ruolo jedi 
(quindi il maestroJedi può fare almeno tutto quello che può fare uno jedi);
attribuire al ruolo jedi tutti i privilegi sulla tabella studenti;
attribuire al maestroJedi tutti i privilegi sulla tabella corsi, 
oltre a tutti i privilegi sulla tabella studenti, sfruttando la gerachia precedentemente definita;
attribuire il ruolo jedi a luke e il ruolo maestroJedi a yoda;
eseguendo opportune query (eventualmente anche sul catalogo)
 provare a capire se luke e yoda hanno adesso i privilegi che vi aspettate.
*/


CREATE ROLE jedi;
CREATE ROLE maestroJedi;

REVOKE SELECT ON TABLE corsi,studenti FROM yoda,luke RESTRICT;

GRANT jedi TO maestroJedi;

GRANT ALL PRIVILEGES ON TABLE studenti TO jedi;
GRANT ALL PRIVILEGES ON TABLE corsi TO maestroJedi;

GRANT jedi TO luke;
GRANT maestroJedi TO yoda;

SET ROLE yoda;
SET search_path TO 'unicorsi';
select * from studenti;

--come previsto yoda ha i privilegi di select su studenti e corsi,
--mentre luke ha i privilegi su studenti. 
