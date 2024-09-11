--- Progetto BD 23-24 12 CFU
--- Numero gruppo 43
--- Nomi e matricole componenti Eugenio Vassallo 5577783, Mario Biberia 5608210, Umeshan pachabalasingham 5606614



--- PARTE III 
/* il file deve essere file SQL ... cio� formato solo testo e apribili ed eseguibili in pgAdmin */



/*************************************************************************************************************************************************************************/ 
--1b. Schema per popolamento in the large
/*************************************************************************************************************************************************************************/ 
SET search_path TO "UniGe_Social_Sport";

CREATE TABLE Utenti_CL (
    utente_id SERIAL,
    nome_utente VARCHAR(50),
    password VARCHAR(50),
    nome VARCHAR(50),
    cognome VARCHAR(50),
    genere VARCHAR(1) CHECK (genere IN ('M', 'F')),
    anno_nascita INTEGER,
    luogo_nascita VARCHAR(100),
    foto BYTEA,
    telefono BIGINT CHECK (telefono >= 0000000000 AND telefono <= 9999999999),
    matricola_studente INTEGER CHECK (matricola_studente >= 0000000 AND matricola_studente <= 9999999), 
    nome_corso VARCHAR(100),
    tipo_utente VARCHAR(10)
);


CREATE TABLE Categorie_CL (
    categoria_id SERIAL,
    nome VARCHAR(50),
    regolamento TEXT,
    numero_giocatori INTEGER,
    foto_esempio BYTEA
);

CREATE TABLE Eventi_CL (
    evento_id SERIAL,
    data_evento DATE,
    stato VARCHAR(10),
    categoria_id INTEGER,
    impianto_id INTEGER
);


/*************************************************************************************************************************************************************************/
--1c. Carico di lavoro
/*************************************************************************************************************************************************************************/ 



/*************************************************************************************************************************************************************************/ 
/* Q1: Query con singola selezione e nessun join */
/*************************************************************************************************************************************************************************/ 


EXPLAIN ANALYZE
SELECT *
FROM Utenti_CL
WHERE nome = 'Nome10000';


/*************************************************************************************************************************************************************************/ 
/* Q2: Query con condizione di selezione complessa e nessun join */
/*************************************************************************************************************************************************************************/ 


EXPLAIN ANALYZE
SELECT *
FROM Utenti_CL
WHERE anno_nascita = 1990 and utente_id > 50000
  AND genere = 'F';


/*************************************************************************************************************************************************************************/ 
/* Q3: Query con almeno un join e almeno una condizione di selezione */
/*************************************************************************************************************************************************************************/ 


EXPLAIN ANALYZE
SELECT e.evento_id, e.data_evento, c.nome AS categoria_nome
FROM Eventi_CL e
JOIN Categorie_CL c ON e.categoria_id = c.categoria_id
WHERE e.stato = 'APERTO';



/*************************************************************************************************************************************************************************/
--1e. Schema fisico
/*************************************************************************************************************************************************************************/ 


/* inserire qui i comandi SQL perla creazione dello schema fisico della base di dati in accordo al risultato della fase di progettazione fisica per il carico di lavoro. */
CREATE INDEX idx_nome ON Utenti_CL(nome);

CREATE INDEX idx_anno_nascita ON Utenti_CL(anno_nascita);


CREATE INDEX idx_eventi_stato ON Eventi_CL(stato);
CREATE INDEX idx_eventi_categoria_id ON Eventi_CL(categoria_id);
CREATE INDEX idx_categorie_categoria_id ON Categorie_CL(categoria_id);



/* inserire qui i comandi SQL per cancellare tutti gli indici gi� esistenti per le tabelle coinvolte nel carico di lavoro */
DROP INDEX IF EXISTS idx_nome;

DROP INDEX IF EXISTS idx_anno_nascita;


DROP INDEX idx_eventi_stato;
DROP INDEX idx_eventi_categoria_id;
DROP INDEX idx_categorie_categoria_id;




/*************************************************************************************************************************************************************************/ 
--2. Controllo dell'accesso 
/*************************************************************************************************************************************************************************/ 

/* inserire qui i comandi SQL per la definizione della politica di controllo dell'accesso della base di dati  (definizione ruoli, gerarchia, definizione utenti, assegnazione privilegi) in modo che, dopo l'esecuzione di questi comandi, 
le operazioni corrispondenti ai privilegi delegati ai ruoli e agli utenti sia correttamente eseguibili. */


-- Creazione ruolo
CREATE ROLE "amministratore";
CREATE ROLE "utente premium";
CREATE ROLE "gestore impianto";
CREATE ROLE "utente semplice";

--Concedere ai ruoli per prima cosa il privilegio di usare lo schema UniGe_Social_Sport
GRANT USAGE ON SCHEMA "UniGe_Social_Sport" TO "amministratore";
GRANT USAGE ON SCHEMA "UniGe_Social_Sport" TO "utente premium";
GRANT USAGE ON SCHEMA "UniGe_Social_Sport" TO "gestore impianto";
GRANT USAGE ON SCHEMA "UniGe_Social_Sport" TO "utente semplice";


--Concedo i vari privilegi ai ruoli
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA "UniGe_Social_Sport" TO "amministratore";


GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA "UniGe_Social_Sport" TO "utente premium";
REVOKE ALL PRIVILEGES ON TABLE Utenti, Impianti,categorie FROM "utente premium";


GRANT ALL PRIVILEGES ON TABLE Impianti TO "gestore impianto";


GRANT SELECT ON Eventi, Tornei TO "utente semplice";
GRANT SELECT, INSERT ON valutazioni TO "utente semplice";

--Creazione utenti e assegnazione ruoli
CREATE USER Pietro WITH PASSWORD 'password123';
GRANT "amministratore" TO Pietro;

CREATE USER Eugenio WITH PASSWORD 'password123';
GRANT "utente premium" TO Eugenio;

CREATE USER Mario WITH PASSWORD 'password123';
GRANT "gestore impianto" TO Mario;

CREATE USER Umeshan WITH PASSWORD 'password123';
GRANT "utente semplice" TO Umeshan;