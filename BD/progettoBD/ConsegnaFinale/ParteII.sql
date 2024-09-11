--- Progetto BD 23-24 12 CFU
--- Numero gruppo 43
--- Nomi e matricole componenti Eugenio Vassallo 5577783, Mario Biberia 5608210, Umeshan pachabalasingham 5606614

--- PARTE 2 
/* il file deve essere file SQL ... cio� formato solo testo e apribili ed eseguibili in pgAdmin */

/*************************************************************************************************************************************************************************/
--1a. Schema
/*************************************************************************************************************************************************************************/ 

CREATE SCHEMA "UniGe_Social_Sport";
SET search_path TO "UniGe_Social_Sport";
SET datestyle TO "MDY";


CREATE TABLE Utenti (
    utente_id SERIAL PRIMARY KEY,
    nome_utente VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    nome VARCHAR(50),
    cognome VARCHAR(50),
    genere VARCHAR(1) CHECK (genere IN ('M', 'F')),
    anno_nascita INTEGER CHECK (anno_nascita > 1900 AND anno_nascita <= EXTRACT(YEAR FROM CURRENT_DATE)),
    luogo_nascita VARCHAR(100),
    foto BYTEA,
    telefono BIGINT CHECK (telefono >= 0000000000 AND telefono <= 9999999999), 
    matricola_studente INTEGER CHECK (matricola_studente >= 0000000 AND matricola_studente <= 9999999), 
    nome_corso VARCHAR(100),
    tipo_utente VARCHAR(10) CHECK (tipo_utente IN ('premium', 'semplice'))
);

CREATE TABLE Categorie (
    categoria_id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    regolamento TEXT,
    numero_giocatori INTEGER CHECK (numero_giocatori > 0),
    foto_esempio BYTEA
);

CREATE TABLE Impianti (
    impianto_id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    via VARCHAR(100) NOT NULL,
    telefono BIGINT CHECK (telefono >= 0000000000 AND telefono <= 9999999999), 
    email VARCHAR(100),
    latitudine DECIMAL(9,6) CHECK (latitudine BETWEEN -90 AND 90),
    longitudine DECIMAL(9,6) CHECK (longitudine BETWEEN -180 AND 180)
);

CREATE TABLE Eventi (
    evento_id SERIAL PRIMARY KEY,
    data_evento DATE,
    stato VARCHAR(10) CHECK (stato IN ('APERTO', 'CHIUSO')),
    categoria_id INTEGER REFERENCES Categorie(categoria_id),
    impianto_id INTEGER REFERENCES Impianti(impianto_id),
    organizzatore_id INTEGER REFERENCES Utenti(utente_id),
    durata_minuti INTEGER CHECK (durata_minuti > 0)
);

CREATE TABLE Iscrizioni (
    iscrizione_id SERIAL PRIMARY KEY,
    evento_id INTEGER REFERENCES Eventi(evento_id),
    utente_id INTEGER REFERENCES Utenti(utente_id),
    data_iscrizione DATE,
    ruolo VARCHAR(10),
    stato VARCHAR(10) CHECK (stato IN ('CONFERMATO', 'RIFIUTATO'))
);

CREATE TABLE Tornei (
    torneo_id SERIAL PRIMARY KEY,
    descrizione TEXT,
    sponsor TEXT,
    premio TEXT,
    restrizioni_partecipazione TEXT,
    modalita_torneo VARCHAR(20) CHECK (modalita_torneo IN ('eliminazione diretta', 'gironi all’italiana', 'mista'))
);

CREATE TABLE Squadre (
    squadra_id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    colore_maglia VARCHAR(50),
    partecipanti_min INTEGER CHECK (partecipanti_min > 0),
    partecipanti_max INTEGER CHECK (partecipanti_max >= partecipanti_min),
    descrizione TEXT,
    note TEXT,
    creato_da INTEGER REFERENCES Utenti(utente_id)
);

CREATE TABLE MembriSquadra (
    membro_squadra_id SERIAL PRIMARY KEY,
    squadra_id INTEGER REFERENCES Squadre(squadra_id),
    utente_id INTEGER REFERENCES Utenti(utente_id),
    ruolo VARCHAR(50),
    stato VARCHAR(10) CHECK (stato IN ('accettato', 'in attesa'))
);

CREATE TABLE RisultatiEvento (
    risultato_evento_id SERIAL PRIMARY KEY,
    evento_id INTEGER REFERENCES Eventi(evento_id),
    punteggio_squadra1 INTEGER CHECK (punteggio_squadra1 >= 0),
    punteggio_squadra2 INTEGER CHECK (punteggio_squadra2 >= 0)
);

CREATE TABLE PrestazioniGiocatore (
    prestazione_id SERIAL PRIMARY KEY,
    risultato_evento_id INTEGER REFERENCES RisultatiEvento(risultato_evento_id),
    utente_id INTEGER REFERENCES Utenti(utente_id),
    punti_segnati INTEGER CHECK (punti_segnati >= 0)
);

CREATE TABLE Valutazioni (
    valutazione_id SERIAL PRIMARY KEY,
    valutatore_id INTEGER REFERENCES Utenti(utente_id),
    valutato_id INTEGER REFERENCES Utenti(utente_id),
    evento_id INTEGER REFERENCES Eventi(evento_id),
    data_valutazione DATE,
    punteggio INTEGER CHECK (punteggio BETWEEN 0 AND 10),
    commento TEXT
);


CREATE TABLE Livelli (
    livello_id SERIAL PRIMARY KEY,
    utente_id INTEGER REFERENCES Utenti(utente_id),
    sport VARCHAR(50) NOT NULL,
    livello INTEGER CHECK (livello BETWEEN 0 AND 100) DEFAULT 60,
    data_aggiornamento DATE DEFAULT CURRENT_DATE
);


CREATE TABLE EventiTorneo (
    evento_torneo_id SERIAL PRIMARY KEY,
    torneo_id INTEGER REFERENCES Tornei(torneo_id),
    evento_id INTEGER REFERENCES Eventi(evento_id)
);

CREATE TABLE SquadreTorneo (
    squadra_torneo_id SERIAL PRIMARY KEY,
    torneo_id INTEGER REFERENCES Tornei(torneo_id),
    squadra_id INTEGER REFERENCES Squadre(squadra_id)
);

/*************************************************************************************************************************************************************************/ 
--1b. Popolamento 
/*************************************************************************************************************************************************************************/ 


INSERT INTO Utenti (utente_id, nome_utente, password, nome, cognome,genere, anno_nascita, luogo_nascita, foto, telefono, matricola_studente, nome_corso, tipo_utente) VALUES
(1,'maria.rossi', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(2,'luigi.bianchi', 'password456', 'Luigi', 'Bianchi', 'M', 1992, 'Genova', NULL, '0987654321', '67890', 'Ingegneria', 'semplice'),
(3,'giovanna.verdi', 'password789', 'Giovanna', 'Verdi','F', 1991, 'Genova', NULL, '0987654321', '67890', 'Ingegneria', 'semplice');

INSERT INTO Categorie (categoria_id ,nome, regolamento, numero_giocatori, foto_esempio) VALUES
(1,'Calcio', 'Regole del calcio', 22, NULL),
(2,'Pallavolo', 'Regole della pallavolo', 12, NULL),
(3, 'Tennis', 'Regole del tennis', 2, NULL),
(5, 'Basket', 'Regole del basket', 10, NULL);

INSERT INTO Impianti (impianto_id ,nome, via, telefono, email, latitudine, longitudine) VALUES
(1,'CUS Genova', 'Via carlo felice 21', '0101234567', 'info@cusgenova.it', 44.4063, 8.9339),
(2,'Impianto Sportivo', 'Via San Vincenzo 34', '0107654321', 'contatti@impiantosportivo.it', 44.4095, 8.9328);

INSERT INTO Eventi (evento_id ,data_evento, stato, categoria_id, impianto_id, organizzatore_id, durata_minuti) VALUES
(1,'2024-08-20', 'APERTO', 1, 1, 1, 90),
(2,'2024-08-22', 'APERTO', 2, 2, 2, 60),
(3,'2024-07-10', 'CHIUSO', 2, 2, 1, 90);

INSERT INTO Iscrizioni (evento_id, utente_id, data_iscrizione, ruolo, stato) VALUES
(1, 1, '2024-07-10', 'giocatore', 'CONFERMATO'),
(1, 2, '2024-07-12', 'arbitro', 'CONFERMATO'),
(1, 3, '2024-07-12', 'giocatore', 'CONFERMATO'),
(2, 1, '2024-07-10', 'giocatore', 'CONFERMATO'),
(2, 2, '2024-07-12', 'arbitro', 'CONFERMATO'),
(2, 3, '2024-07-12', 'giocatore', 'RIFIUTATO');

INSERT INTO Tornei (descrizione, sponsor, premio, restrizioni_partecipazione, modalita_torneo) VALUES
('Torneo estivo di calcio', 'Sponsor A', 'Coppa e medaglie', 'Nessuna restrizione', 'eliminazione diretta'),
('Torneo invernale di pallavolo', 'Sponsor B', 'Buono acquisto', 'Solo studenti UniGe', 'gironi all’italiana');

INSERT INTO Squadre (nome, colore_maglia, partecipanti_min, partecipanti_max, descrizione, note, creato_da) VALUES
('Team A', 'Rosso', 5, 10, 'Squadra A di calcio', 'Note a', 1),
('Team B', 'Blu', 6, 12, 'Squadra B di pallavolo', 'Note B',  1);

INSERT INTO MembriSquadra (squadra_id, utente_id, ruolo, stato) VALUES
(1, 1, 'attaccante', 'accettato'),
(2, 2, 'difensore', 'accettato'),
(1, 3, 'difensore', 'in attesa');

INSERT INTO RisultatiEvento (evento_id, punteggio_squadra1, punteggio_squadra2) VALUES
(1, 2, 3),
(2, 1, 1);

INSERT INTO PrestazioniGiocatore (risultato_evento_id, utente_id, punti_segnati) VALUES
(1, 2, 1),
(2, 1, 0);


INSERT INTO Valutazioni (valutatore_id, valutato_id, evento_id, data_valutazione, punteggio, commento) VALUES
(2, 1, 2, '2024-07-23', 1, 'Sufficiente');

INSERT INTO Livelli (utente_id, sport, livello, data_aggiornamento) VALUES
(1, 'Calcio', 70, '2024-07-21'),
(1, 'Pallavolo', 50, '2024-07-21'),
(2, 'Calcio', 60, '2024-07-21'),
(2, 'Pallavolo', 40, '2024-07-21');

INSERT INTO EventiTorneo (torneo_id, evento_id) VALUES
(1, 1),
(2, 2);

INSERT INTO SquadreTorneo (torneo_id, squadra_id) VALUES
(1, 1),
(2, 2);

/*************************************************************************************************************************************************************************/ 
--2. Vista
--Vista Programma che per ogni impianto e mese riassume tornei e eventi che si svolgono in tale impianto, evidenziando in particolare per ogni categoria il numero di tornei, il numero di eventi, il numero di partecipanti coinvolti e di quanti diversi corsi di studio, la durata totale (in termini di minuti) di utilizzo e la percentuale di utilizzo rispetto alla disponibilit� complessiva (minuti totali nel mese in cui l�impianto � utilizzabile) 
/*************************************************************************************************************************************************************************/ 

CREATE VIEW Programma AS
SELECT 
    f.nome AS nome_impianto,
    f.impianto_id AS impianto_id, 
    EXTRACT(YEAR FROM e.data_evento) AS anno,
    EXTRACT(MONTH FROM e.data_evento) AS mese,
    c.nome AS nome_categoria,
    COUNT(DISTINCT et.torneo_id) AS numero_tornei,
    COUNT(DISTINCT e.evento_id) AS numero_eventi,
    COUNT(DISTINCT r.utente_id) AS numero_partecipanti,
    COUNT(DISTINCT u.nome_corso) AS numero_corsi,
    SUM(e.durata_minuti) AS durata_totale_minuti,
    (SUM(e.durata_minuti) / 
        (EXTRACT(DAY FROM DATE_TRUNC('month', DATE_TRUNC('month', e.data_evento)) + INTERVAL '1 month' - INTERVAL '1 day') * 24 * 60) * 100) AS percentuale_utilizzo
FROM 
    Eventi e
    LEFT JOIN Iscrizioni r ON e.evento_id = r.evento_id
    LEFT JOIN Utenti u ON r.utente_id = u.utente_id
    LEFT JOIN Impianti f ON e.impianto_id = f.impianto_id
    LEFT JOIN Categorie c ON e.categoria_id = c.categoria_id
    LEFT JOIN EventiTorneo et ON e.evento_id = et.evento_id
GROUP BY f.nome, f.impianto_id, EXTRACT(YEAR FROM e.data_evento), EXTRACT(MONTH FROM e.data_evento), c.nome, DATE_TRUNC('month', e.data_evento);




/*************************************************************************************************************************************************************************/ 
--3. Interrogazioni
/*************************************************************************************************************************************************************************/ 

/*************************************************************************************************************************************************************************/ 
/* 3a: Determinare gli utenti che si sono candidati come giocatori e non sono mai stati accettati e quelli che sono stati accettati tutte le volte che si sono candidati */
/*************************************************************************************************************************************************************************/ 

/* Utenti che si sono candidati come giocatori e non sono mai stati accettati */
SELECT u.nome_utente
FROM Utenti u
LEFT JOIN Iscrizioni r ON u.utente_id = r.utente_id
WHERE r.ruolo = 'giocatore'
GROUP BY u.nome_utente
HAVING SUM(CASE WHEN r.stato = 'CONFERMATO' THEN 1 ELSE 0 END) = 0
   AND COUNT(r.iscrizione_id) > 0;

/* Utenti che sono stati accettati tutte le volte che si sono candidati */
SELECT u.nome_utente
FROM Utenti u
LEFT JOIN Iscrizioni r ON u.utente_id = r.utente_id
WHERE r.ruolo = 'giocatore'
GROUP BY u.nome_utente
HAVING SUM(CASE WHEN r.stato = 'RIFIUTATO' THEN 1 ELSE 0 END) = 0
   AND COUNT(r.iscrizione_id) > 0;

/*************************************************************************************************************************************************************************/ 
/* 3b: determinare gli utenti che hanno partecipato ad almeno un evento di ogni categoria */
/*************************************************************************************************************************************************************************/ 

SELECT u.nome_utente
FROM Utenti u
WHERE NOT EXISTS (
    SELECT c.categoria_id
    FROM Categorie c
    WHERE NOT EXISTS (
        SELECT r.iscrizione_id
        FROM Iscrizioni r
        JOIN Eventi e ON r.evento_id = e.evento_id
        WHERE r.utente_id = u.utente_id AND e.categoria_id = c.categoria_id
    )
);

/*************************************************************************************************************************************************************************/ 
/* 3c: determinare per ogni categoria il corso di laurea pi� attivo in tale categoria, cio� quello i cui studenti hanno partecipato al maggior numero di eventi (singoli o all�interno di tornei) di tale categoria */
/*************************************************************************************************************************************************************************/ 

WITH PartecipazionePerCorso AS (
    SELECT 
        c.nome AS nome_categoria, 
        u.nome_corso, 
        COUNT(*) AS numero_partecipanti
    FROM Eventi e
    JOIN Iscrizioni r ON e.evento_id = r.evento_id
    JOIN Utenti u ON r.utente_id = u.utente_id
    JOIN Categorie c ON e.categoria_id = c.categoria_id
    GROUP BY c.nome, u.nome_corso
)

SELECT 
    nome_categoria, 
    nome_corso, 
    numero_partecipanti
FROM PartecipazionePerCorso
WHERE (nome_categoria, numero_partecipanti) IN (
    SELECT 
        nome_categoria, 
        MAX(numero_partecipanti)
    FROM PartecipazionePerCorso
    GROUP BY nome_categoria
)
ORDER BY nome_categoria;

/*************************************************************************************************************************************************************************/ 
--4. Funzioni
/*************************************************************************************************************************************************************************/ 

/*************************************************************************************************************************************************************************/ 
/* 4a: funzione che effettua la conferma di un giocatore quale componente di una squadra, realizzando gli opportuni controlli */
/*************************************************************************************************************************************************************************/ 

CREATE OR REPLACE FUNCTION conferma_giocatore_squadra(p_squadra_id INTEGER, p_utente_id INTEGER) RETURNS VOID AS $$
BEGIN
    -- Controlla se il giocatore è in attesa di conferma nella squadra specificata
    IF EXISTS (
        SELECT 1 
        FROM MembriSquadra 
        WHERE squadra_id = p_squadra_id 
        AND utente_id = p_utente_id 
        AND stato = 'in attesa'
    ) THEN
        -- Aggiorna lo stato del giocatore a 'accettato'
        UPDATE MembriSquadra 
        SET stato = 'accettato' 
        WHERE squadra_id = p_squadra_id 
        AND utente_id = p_utente_id;
    ELSE
        -- Genera un'eccezione se il giocatore non è stato trovato o è già stato confermato
        RAISE EXCEPTION 'Membro della squadra non trovato o già confermato';
    END IF;
END;
$$ LANGUAGE plpgsql;

/* 
DO $$ 
test per la funzione conferma_giocatore_squadra

questa da errore perche' il giocatore 1 e gia' stato confermato nella squadra 1
BEGIN
    PERFORM conferma_giocatore_squadra(1, 1);
END $$;


questa invece funziona perche' il giocatore 3 e' in attesa di conferma nella squadra 1
DO $$ 
BEGIN
    PERFORM conferma_giocatore_squadra(1, 3);
END $$;
*/


/*************************************************************************************************************************************************************************/ 
/* 4b1: funzione che dato un giocatore ne calcoli il livello */

/* 4b2: funzione corrispondente alla seguente query parametrica: data una categoria e un corso di studi, determinare la frazione di partecipanti a eventi di quella categoria di genere femminile sul totale dei partecipanti provenienti da quel corso di studi */
/*************************************************************************************************************************************************************************/ 

CREATE OR REPLACE FUNCTION calcola_livello_giocatore(utente_id INTEGER) RETURNS INTEGER AS $$
DECLARE
    livello INTEGER := 60; -- Livello iniziale di default
BEGIN
    -- Calcola il livello basato sulla media dei punteggi ricevuti
    SELECT COALESCE(ROUND(AVG(punteggio)), 60) INTO livello
    FROM Valutazioni
    WHERE valutato_id = utente_id;

    RETURN livello;
END;
$$ LANGUAGE plpgsql;


/*
test per la funzione e stampa il risultato
DO $$ 
DECLARE
    livello INTEGER;
BEGIN
    livello := calcola_livello_giocatore(1);
    RAISE NOTICE 'Il livello del giocatore è %', livello;
END $$;
*/


CREATE OR REPLACE FUNCTION frazione_partecipanti_femminili(categoria_nome VARCHAR, corso_studi_nome VARCHAR) RETURNS DECIMAL AS $$
DECLARE
    totale_partecipanti INTEGER;
    partecipanti_femminili INTEGER;
    frazione DECIMAL;
BEGIN
    -- Calcola il totale dei partecipanti della categoria e del corso di studi
    SELECT COUNT(*) INTO totale_partecipanti
    FROM Iscrizioni r
    JOIN Eventi e ON r.evento_id = e.evento_id
    JOIN Utenti u ON r.utente_id = u.utente_id
    JOIN Categorie c ON e.categoria_id = c.categoria_id
    WHERE c.nome = categoria_nome AND u.nome_corso = corso_studi_nome;

    -- Calcola il numero di partecipanti femminili della categoria e del corso di studi
    SELECT COUNT(*) INTO partecipanti_femminili
    FROM Iscrizioni r
    JOIN Eventi e ON r.evento_id = e.evento_id
    JOIN Utenti u ON r.utente_id = u.utente_id
    JOIN Categorie c ON e.categoria_id = c.categoria_id
    WHERE c.nome = categoria_nome AND u.nome_corso = corso_studi_nome AND u.genere = 'F';

    -- Calcola la frazione
    IF totale_partecipanti > 0 THEN
        frazione := partecipanti_femminili::DECIMAL / totale_partecipanti;
    ELSE
        frazione := 0;
    END IF;

    RETURN frazione;
END;
$$ LANGUAGE plpgsql;

/*
test per la funzione e stampa il risultato
select frazione_partecipanti_femminili('Calcio', 'Ingegneria');
*/

/*************************************************************************************************************************************************************************/ 
--5. Trigger
/*************************************************************************************************************************************************************************/ 

/*************************************************************************************************************************************************************************/ 
/* 5a: trigger per la verifica del vincolo che non � possibile iscriversi a eventi chiusi e che lo stato di un evento sportivo diventa CHIUSO quando si raggiunge un numero di giocatori pari a quello previsto dalla categoria */
/*************************************************************************************************************************************************************************/ 

CREATE OR REPLACE FUNCTION verifica_iscrizione_evento() RETURNS TRIGGER AS $$
BEGIN
    -- Verifica se l'evento è chiuso
    IF (SELECT stato FROM Eventi WHERE evento_id = NEW.evento_id) = 'CHIUSO' THEN
        RAISE EXCEPTION 'Non è possibile iscriversi a un evento chiuso';
    END IF;

    -- Verifica se il numero di giocatori confermati ha raggiunto il numero previsto dalla categoria
    IF (SELECT COUNT(*) FROM Iscrizioni WHERE evento_id = NEW.evento_id AND stato = 'CONFERMATO') >= 
       (SELECT c.numero_giocatori FROM Eventi e JOIN Categorie c ON e.categoria_id = c.categoria_id WHERE e.evento_id = NEW.evento_id) THEN
        RAISE NOTICE 'Numero massimo di giocatori confermati raggiunto';
        UPDATE Eventi SET stato = 'CHIUSO' WHERE evento_id = NEW.evento_id; 
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verifica_iscrizione_evento
AFTER INSERT OR UPDATE ON Iscrizioni
FOR EACH ROW
WHEN (NEW.stato = 'CONFERMATO')
EXECUTE FUNCTION verifica_iscrizione_evento();

/*
--test per il trigger
INSERT INTO Utenti (utente_id, nome_utente, password, nome, cognome,genere, anno_nascita, luogo_nascita, foto, telefono, matricola_studente, nome_corso, tipo_utente) VALUES
(11,'test1', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(12,'test2', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(13,'test3', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(14,'test4', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(15,'test5', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(16,'test6', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(17,'test7', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(18,'test8', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(19,'test9', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(20,'test10', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(21,'test11', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(22,'test12', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium'),
(23,'test13', 'password123', 'Maria', 'Rossi', 'F' , 1990, 'Genova', NULL, '1234567890', '12345', 'Informatica', 'premium');

INSERT INTO Eventi (evento_id ,data_evento, stato, categoria_id, impianto_id, organizzatore_id, durata_minuti) VALUES
(3,'2024-08-22', 'APERTO', 2, 2, 2, 60);

INSERT INTO Iscrizioni (evento_id, utente_id, data_iscrizione, ruolo, stato) VALUES
(3, 11, '2024-07-10', 'giocatore', 'CONFERMATO'),
(3, 12, '2024-07-10', 'giocatore', 'CONFERMATO'),
(3, 13, '2024-07-10', 'giocatore', 'CONFERMATO'),
(3, 14, '2024-07-10', 'giocatore', 'CONFERMATO'),
(3, 15, '2024-07-10', 'giocatore', 'CONFERMATO'),
(3, 16, '2024-07-10', 'giocatore', 'CONFERMATO'),
(3, 17, '2024-07-10', 'giocatore', 'CONFERMATO'),
(3, 18, '2024-07-10', 'giocatore', 'CONFERMATO'),
(3, 19, '2024-07-10', 'giocatore', 'CONFERMATO'),   
(3, 20, '2024-07-10', 'giocatore', 'CONFERMATO'),
(3, 21, '2024-07-10', 'giocatore', 'CONFERMATO');


INSERT INTO Iscrizioni (evento_id, utente_id, data_iscrizione, ruolo, stato) VALUES
(3, 22, '2024-07-10', 'giocatore', 'CONFERMATO');


select * from Eventi where evento_id = 3;

l'evento 3 e' stato chiuso perche' il numero di giocatori confermati ha raggiunto il numero previsto dalla categoria'

INSERT INTO Iscrizioni (evento_id, utente_id, data_iscrizione, ruolo, stato) VALUES
(3, 23, '2024-07-10', 'giocatore', 'CONFERMATO');
soleva un eccezione perche' l'evento e' chiuso
*/

/*************************************************************************************************************************************************************************/ 
/* 5b1: trigger che gestisce la sede di un evento: se la sede � disponibile nel periodo di svolgimento dell�evento la sede viene confermata altrimenti viene individuata una sede alternativa: tra gli impianti disponibili nel periodo di svolgimento dell�evento si seleziona quello meno utilizzato nel mese in corso (vedi vista Programma) */

/* 5b2: trigger per il mantenimento dell�attributo derivato livello */
/*************************************************************************************************************************************************************************/ 

CREATE OR REPLACE FUNCTION gestisci_sede_evento() RETURNS TRIGGER AS $$
DECLARE
    sede_alternativa INTEGER;
BEGIN
    -- Verifica se la sede originale è disponibile
    IF EXISTS (
        SELECT 1 
        FROM Eventi 
        WHERE impianto_id = NEW.impianto_id 
          AND data_evento = NEW.data_evento 
          AND evento_id <> NEW.evento_id
    ) THEN
        -- Trova una sede alternativa disponibile e meno utilizzata dal Programma view
        SELECT p.impianto_id
        INTO sede_alternativa
        FROM Programma p
        WHERE p.anno = EXTRACT(YEAR FROM NEW.data_evento)
          AND p.mese = EXTRACT(MONTH FROM NEW.data_evento)
          AND p.impianto_id <> NEW.impianto_id
          AND NOT EXISTS (
            SELECT 1 
            FROM Eventi e 
            WHERE e.impianto_id = p.impianto_id 
              AND e.data_evento = NEW.data_evento
        )
        ORDER BY p.percentuale_utilizzo ASC
        LIMIT 1;

        RAISE NOTICE 'Selected alternative facility: %', sede_alternativa;

        IF sede_alternativa IS NOT NULL THEN
            -- Assegna la sede alternativa
            NEW.impianto_id = sede_alternativa;
        ELSE
            -- Se non ci sono sedi alternative disponibili, solleva un'eccezione
            RAISE EXCEPTION 'Nessuna sede disponibile per la data dell''evento';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_gestisci_sede_evento
BEFORE INSERT OR UPDATE ON Eventi
FOR EACH ROW
EXECUTE FUNCTION gestisci_sede_evento();



/*
--test per il trigger
INSERT INTO Eventi (evento_id ,data_evento, stato, categoria_id, impianto_id, organizzatore_id, durata_minuti) VALUES
(4,'2024-07-20', 'APERTO', 1, 1, 1, 90);

-- questo inserimento sara modificato perche' la sede originale non è disponibile
INSERT INTO Eventi (evento_id ,data_evento, stato, categoria_id, impianto_id, organizzatore_id, durata_minuti) VALUES
(5,'2024-07-20', 'APERTO', 2, 1, 1, 90);

-- questo inserimento non sara modificato perche la sede e disponibile
INSERT INTO Eventi (evento_id ,data_evento, stato, categoria_id, impianto_id, organizzatore_id, durata_minuti) VALUES
(6,'2024-09-20', 'APERTO', 1, 1, 1, 90);

*/


CREATE OR REPLACE FUNCTION aggiorna_livello_utente() 
RETURNS TRIGGER AS $$
DECLARE
    sport_nome VARCHAR(50);
    nuovo_livello INTEGER;
BEGIN
    -- Ottenere il nome dello sport tramite join tra Eventi e Categorie
    SELECT c.nome INTO sport_nome
    FROM Eventi e
    JOIN Categorie c ON e.categoria_id = c.categoria_id
    WHERE e.evento_id = NEW.evento_id;

    -- Calcolare il nuovo livello dell'utente per lo sport specifico
    SELECT ROUND(AVG(v.punteggio) *10) INTO nuovo_livello
    FROM Valutazioni v
    JOIN Eventi e ON v.evento_id = e.evento_id
    JOIN Categorie c ON e.categoria_id = c.categoria_id
    WHERE v.valutato_id = NEW.valutato_id AND c.nome = sport_nome;

    -- Aggiornare il livello dell'utente per lo sport specifico
    UPDATE Livelli
    SET livello = nuovo_livello,
        data_aggiornamento = CURRENT_DATE
    WHERE utente_id = NEW.valutato_id AND sport = sport_nome;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per aggiornare il livello dell'utente dopo l'inserimento o l'aggiornamento su Valutazioni
CREATE TRIGGER trg_aggiorna_livello_utente
AFTER INSERT OR UPDATE ON Valutazioni
FOR EACH ROW
EXECUTE FUNCTION aggiorna_livello_utente();



/*
--test per il trigger
INSERT INTO Valutazioni (valutatore_id, valutato_id, evento_id, data_valutazione, punteggio, commento) VALUES
(2, 1, 1, '2024-07-21', 1, 'Prestazione eccezionale');
*/