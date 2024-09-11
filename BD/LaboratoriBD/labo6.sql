set search_path to unicorsi;

--Specificare attraverso un vincolo CHECK che un esame
--non può essere sostenuto in data successiva alla data odierna.
--Si riesce ad aggiungere tale vincolo? Perchè?


alter table esami
add constraint esami_data_check CHECK (data < CURRENT_DATE+1);


-- Specificare attraverso un vincolo CHECK che un esame non può essere sostenuto in data precedente 
-- il 1 gennaio 2014. Si riesce ad aggiungere tale vincolo? Perchè?

-- alter table esami 
-- add constraint esami_data_prev_check CHECK (data > '2014-01-01')
-- alcune tuple presenta esami sostenuti prima del 2014-01-01
-- ERROR:  check constraint "esami_data_prev_check" of relation "esami" is violated by some row 

-- Specificare attraverso un vincolo CHECK che non è mai possibile che il relatore
-- non sia specificato (relatore nullo) per uno studente che ha già iniziato la tesi
-- ( laurea non nulla)


alter table studenti
add constraint studenti_relatore_check CHECK (relatore != NULL AND laurea = null );


--Inserire nella relazione Professori:

-- (a)  i dati relativi al Professore Prini Gian Franco con identificativo 38 e stipendio 50000 euro;

-- (b)  i dati relativi alla Professoressa Stefania Bandini, con identificativo 39, senza specificare un valore per stipendio;

-- (c)  i dati relativi alla Professorressa Rosti, con identificativo 40, senza specificare nome proprio né stipendio.
-- I comandi vanno a buon fine? Perchè?

insert into professori values
(38, 'Prini', 'Gian Franco', 50000);
insert into professori values
(39, 'Bandini', 'Stefania'); -- da implementazione viene aggiunte il valore di default -> Stipendio decimal(8,2) NOT NULL DEFAULT 15000 CHECK (Stipendio >=0)
-- (40, 'Rosti') -- la colonna Nome deve avere un valore 

-- Aumentare di 5000 euro lo stipendio dei Professori che hanno uno stipendio inferiore a 15000 euro.

update professori
set stipendio = stipendio + 5000
where stipendio < 15000;


-- Rimuovere il vincolo not null su Esami.voto mediante il comando alter table esami alter column voto drop not null;

ALTER TABLE Esami
ALTER COLUMN Voto DROP NOT NULL;


/*
--Inserire ora il corso di ’Laboratorio di Informatica’ (id ’labinfo’) per il corso di laurea di Informatica
--(id corso di laurea 9).
*/

insert into corsi values
('labinfo', 9, 'laboratorio di infomatica' );

--Inserire il fatto che gli studenti di Informatica non ancora in tesi hanno sostenuto
--tale esame in data odierna (senza inserire votazione).

insert into esami(studente, corso, data, voto) 
SELECT matricola, 'labinfo', CURRENT_DATE, NULL
FROM studenti
WHERE corsodilaurea = 9 AND laurea IS NULL;

/*
Modificare i voti degli studenti che hanno sostenuto 
tale corso e non hanno assegnata una votazione assegnando come votazione la votazione media dello studente.
*/


update esami 
set voto = (  
  SELECT AVG(voto) 
  FROM esami 
  INNER JOIN studenti ON studenti.matricola = esami.studente
  WHERE studenti.corsodilaurea = 9 AND studenti.laurea IS NOT NULL
)
where voto is null;


/*
Ripristinare, se possibile, il vincolo not null su Esami.voto, ad es. mediante il comando alter table esami 
add constraint vnn check (voto is not null); 
*/

ALTER TABLE Esami
ADD CONSTRAINT voto_not_null CHECK (voto IS NOT NULL);

/*
Creare una vista StudentiNonInTesi che permetta di visualizzare 
i dati (matricola, cognome, nome, residenza, data di nascita, 
luogo di nascita, corso di laurea, anno accademico di iscrizione) 
degli studenti non ancora in tesi (che non hanno assegnato alcun relatore).
*/


CREATE VIEW StudentiNonInTesi AS
SELECT matricola, cognome, nome, residenza, datanascita, luogonascita, corsodilaurea, iscrizione
FROM studenti
WHERE relatore IS NULL;


/*
Interrogare la vista StudentiNonInTesi per determinare gli studenti 
non in tesi nati e residenti a Genova.
*/


SELECT *
FROM StudentiNonInTesi
WHERE luogonascita = 'Genova' AND residenza = 'Genova';


/*
Creare la vista StudentiMate degli studenti di matematica non ancora laureati 
in cui ad ogni studente sono associate le informazioni sul numero di esami che 
ha sostenuto e la votazione media conseguita. Nella vista devono comparire anche 
gli studenti che non hanno sostenuto alcun esame.
*/


CREATE VIEW StudentiMate AS
SELECT studenti.matricola, studenti.cognome, studenti.nome, COUNT(esami.voto) AS numero_esami, AVG(esami.voto) AS media_voto
FROM studenti  
LEFT JOIN esami ON studenti.matricola = esami.studente
WHERE studenti.corsodilaurea = 1 AND studenti.laurea is null
GROUP BY studenti.matricola , studenti.cognome, studenti.nome;


/*
Utilizzando la vista StudentiMate determinare quanti esami hanno 
sostenuto complessivamente gli studenti di matematica non ancora laureati
*/



SELECT SUM(numero_esami) AS total_esami
FROM StudentiMate;


/*	
Inserire una tupla a vostra scelta nella vista StudentiNonInTesi. 
L'inserimento va a buon fine? Perché? Esaminare l'effetto dell'inserimento,
 se andato a buon fine, sulla tabella Studenti
*/


INSERT INTO StudentiNonInTesi (matricola, cognome, nome, residenza, datanascita, luogonascita, corsodilaurea,iscrizione)
VALUES ('123456789', 'johnson', 'Dwayne', 'Genova', '12/23/1972', 'California', '1', '2020');

--L'inserimento va a buon fine poichè la vista contiene tutte le colone che non devono essere vuoti

/*	
Inserire una tupla a piacere nella vista StudentiMate. 
L'inserimento va a buon fine? Perché? Esaminare l'effetto dell'inserimento,
se andato a buon fine, sulla tabella Studenti.
*/

/*
INSERT INTO StudentiMate (matricola, nome, cognome)
VALUES ('WWE', 'John', 'Cena')
*/
--L'inserimento non va a buon fine poichè la vista non contiene 
--tutti i valori per creare una tupla studenti valida