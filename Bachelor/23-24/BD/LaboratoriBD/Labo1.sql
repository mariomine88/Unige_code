CREATE SCHEMA "corsi";

set search_path to "videoteca";

CREATE TABLE "professori"
	(id DECIMAL(5) PRIMARY KEY,
	Cognome VARCHAR(20) NOT NULL,
	Nome VARCHAR(20) NOT NULL,
	Stipendio NUMERIC(6,2) DEFAULT 15000,
	Incongedo BOOL DEFAULT FALSE,
	UNIQUE(Cognome,Nome));


--insert into professori values (123456, 'pippo', 'pluto', NULL, TRUE); inserimento con id di 6 cifre e non 5
--ERRORE:  il campo numeric causa un overflow

--insert into professori values (12345, 'pippo', 'pluto', NULL, TRUE); inserisco due volte la stessa tupla
--insert into professori values (12345, 'pippo', 'pluto', NULL, TRUE);
--ERRORE:  un valore chiave duplicato viola il vincolo univoco "professori_pkey"

insert into professori values (54661, 'guerrini', 'giovanna', 1256.78, FALSE);
insert into professori values (55777, 'eugenio', 'vassallo', 1130.50, FALSE);
insert into professori values (56679, 'mario', 'biberia', 0001.00, FALSE);

CREATE TABLE "Corsi" 
	(id CHAR(10) PRIMARY KEY,
	 CorsoDiLaurea VARCHAR(50) NOT NULL,
	 Nome VARCHAR(50) NOT NULL,
	 Professore DECIMAL(5),
	 Attivato BOOLEAN DEFAULT FALSE,
     FOREIGN KEY (Professore) REFERENCES professori(id) ON UPDATE CASCADE ON DELETE RESTRICT;
	);

-- Inserimento di tuple relative a corsi di Programmazione, Calculus e Algebra (inserimenti corretti)
INSERT INTO "Corsi" (id, CorsoDiLaurea, Nome, Professore, Attivato) 
VALUES 
    ('001P123456', 'Informatica', 'Programmazione', '55777', TRUE),
    ('002C123457', 'Matematica', 'Calculus', '12345', TRUE),
    ('003A123458', 'Matematica', 'Algebra', '54661', TRUE);

--nota: se voglio eliminare una riga, ad esempio un corso con id = '1111111111' che avevo creato come test
--scrivo: DELETE FROM "Corsi" WHERE id = '1111111111';

--test vincoli:

-- Tentativo di inserire una tupla che viola il vincolo di integrità referenziale
-- (assegnando un identificatore di professore che non esiste)
INSERT INTO "Corsi" (id, CorsoDiLaurea, Nome, Professore, Attivato) 
VALUES 
    ('004X123459', 'Fisica', 'Meccanica Quantistica', '55555', TRUE);
--ERROR:  La chiave (professore)=(55555) non è presente nella tabella "professori".la INSERT o l'UPDATE sulla tabella "Corsi" viola il vincolo di chiave esterna "Corsi_professore_fkey" 

--test cancellazione di un professore che è referenziato in un corso (non si può fare perchè la chiave esterna ha "on delete restrict")
DELETE FROM professori where id = '55777';
--ERROR:  La chiave (id)=(55777) è ancora referenziata dalla tabella "Corsi".l'istruzione UPDATE o DELETE sulla tabella "professori" viola il vincolo di chiave esterna "Corsi_professore_fkey" sulla tabella "Corsi" 
