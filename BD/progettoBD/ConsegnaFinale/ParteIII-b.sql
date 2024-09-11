--- Progetto BD 23-24 12 CFU
--- Numero gruppo 43
--- Nomi e matricole componenti Eugenio Vassallo 5577783, Mario Biberia 5608210, Umeshan pachabalasingham 5606614


--- PARTE III 
/* il file deve essere file SQL ... cio� formato solo testo e apribili ed eseguibili in pgAdmin */


/*************************************************************************************************************************************************************************/ 
--1f. Popolamento in the large
/*************************************************************************************************************************************************************************/ 
SET search_path TO "UniGe_Social_Sport";

DO $$
DECLARE
    i INTEGER;
BEGIN
    -- Popolamento della tabella Utenti_CL
    FOR i IN 1..1000000 LOOP
        INSERT INTO Utenti_CL (
            nome_utente, password, nome, cognome, genere , anno_nascita, luogo_nascita, foto, telefono, matricola_studente, nome_corso, tipo_utente
        ) VALUES (
            'utente' || i,
            'password' || i,
            'Nome' || i,
            'Cognome' || i,
            CASE WHEN i % 2 = 0 THEN 'M' ELSE 'F' END,
            1990 + (i % 30),
            'Città' || i,
            NULL,
            1000000000 + i,
            1000000 + i,
            CASE WHEN i % 2 = 0 THEN 'Informatica' ELSE 'Ingegneria' END,
            CASE WHEN i % 3 = 0 THEN 'premium' ELSE 'semplice' END
        );
    END LOOP;
END $$;

DO $$
DECLARE
    i INTEGER;
BEGIN
    -- Popolamento della tabella Categorie_CL
    FOR i IN 1..50000 LOOP
        INSERT INTO Categorie_CL (
            nome, regolamento, numero_giocatori, foto_esempio
        ) VALUES (
            'Categoria' || i,
            'Regolamento per categoria ' || i,
            5 + (i % 6),
            NULL
        );
    END LOOP;
END $$;

DO $$
DECLARE
    i INTEGER;
BEGIN
    -- Popolamento della tabella Eventi_CL
    FOR i IN 1..500000 LOOP
        INSERT INTO Eventi_CL (
            data_evento, stato, categoria_id, impianto_id
        ) VALUES (
            CURRENT_DATE + ((i % 365) * INTERVAL '1 day'),
            CASE WHEN i % 2 = 0 THEN 'APERTO' ELSE 'CHIUSO' END,
            1 + (i % 50),
            1 + (i % 100)
        );
    END LOOP;
END $$;