/*
1. Creare un trigger ControllaProf con modalità di esecuzione orientata alla tupla per 
garantire che un professore non venga assegnato 
a più di cinque corsi attivi. Nel caso questo accada, si sollevi un’eccezione.
Nota: l’eccezione in PostgreSQL può essere sollevata con il comando RAISE EXCEPTION <stringa>.
La stringa viene scritta in output e l’elaborazione del trigger e dell’evento che lo ha attivato
viene completamente annullata (comportamento transazionale).
*/
SET search_path TO 'unicorsi';

CREATE OR REPLACE FUNCTION ControllaProf() RETURNS TRIGGER AS $$
DECLARE
    active_courses_count INT;
BEGIN
    IF NEW.attivato THEN
        SELECT COUNT(*) INTO active_courses_count
        FROM corsi
        WHERE professore = NEW.professore AND attivato = true;

        IF active_courses_count >= 5 THEN
            RAISE EXCEPTION 'A professor cannot be assigned to more than five active courses.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ControllaProf
BEFORE INSERT OR UPDATE ON corsi
FOR EACH ROW EXECUTE PROCEDURE ControllaProf();

-- Test
-- 2.Assegnare il professore con id 1 al corso con id ’algo1’. Che cosa succede?

UPDATE corsi
SET professore = 1
WHERE id = 'algo1';

-- ERROR:  A professor cannot be assigned to more than five active courses.
-- CONTEXT:  PL/pgSQL function controllaprof() line 10 at RAISE 

select *
from corsi
where professore = 1;

-- fecendo questa query si può vedere che il professore con id 1 ha già 5 corsi attivi

--3.Assegnare il professore con id 15 ai corsi di informatica non
--attivati e il professore con id 1 ai corsi di matematica non attivati.  Che cosa succede e perché?

UPDATE corsi
SET professore = 15
WHERE corsodilaurea = '9' AND attivato = false;

-- Il professore con id 15 aveva già 3 corsi, ci sono 2 corsi di informatica non attivi quindi vengono assegnati a lui

UPDATE corsi
SET professore = 1
WHERE corsodilaurea = '1' AND attivato = false;

-- il professore con id 1 aveva gia 5 corsi attivi ma il nostro trigger non controlla i corsi non attivi quindi non ci sono problemi

/*
4 Assegnare il professore con id 15 ai corsi di matematica non attivati.
 (verificare prima quanti sono). Attivare tutti i corsi non ancora attivi
  (verificare prima quanti sono). Che cosa succede e perché? Quante tuple 
  sono state aggiornate dall'ultimo comando?
*/

-- Controlla quanti corsi di matematica non attivi ci sono

select *
from corsi
WHERE corsodilaurea = '1' AND attivato = false;

-- ritorna 1 corso

-- Assegna il professore con id 15 ai corsi di matematica non attivi

UPDATE corsi
SET professore = 15
WHERE corsodilaurea = '1' AND attivato = false;

-- gli viene assegnato il corso di matematica non attivo ha 6 cosri 3 attivi e 3 non attivi

-- controlla quanti corsi non attivi ci sono

select *
from corsi
WHERE attivato = false;

-- ritorna 5 corsi

-- Attivo tutti i corsi non ancora attivi

UPDATE corsi
SET attivato = true
WHERE attivato = false;

-- da errore perchè il professore con id 15 ha già 5 corsi attivi e uno disattivo e non può averne di più, 
-- il trigger ha fatto il controllo e ha sollevato l'eccezione 
-- e quindi nessun corso è stato attivato.

--5.Cancellare il trigger ControllaProf con il comando DROP TRIGGER ControllaProf ON Corsi.

DROP TRIGGER ControllaProf ON Corsi.

/*
6. Creare nuovamente il trigger ControllaProf con comportamento analogo al precedente ma,
nel caso in cui il vincolo non sia soddisfatto, non sollevare l’eccezione ma notificare
soltanto il fatto ed evitare la modifica delle tuple che hanno portato alla violazione. 
Utilizzare a questo proposito una nuova trigger function.
*/

CREATE OR REPLACE FUNCTION ControllaProfNotify() RETURNS TRIGGER AS $$
DECLARE
    active_courses_count INT;
BEGIN
    IF NEW.attivato THEN
        SELECT COUNT(*) INTO active_courses_count
        FROM corsi
        WHERE professore = NEW.professore AND attivato = true;

        IF active_courses_count >= 5 THEN
            RAISE NOTICE 'A professor cannot be assigned to more than five active courses.'; -- notifica e fa continuare l'esecuzione
            RETURN NULL;  -- evita la modifica della tupla
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ControllaProf
BEFORE INSERT OR UPDATE ON corsi
FOR EACH ROW EXECUTE PROCEDURE ControllaProfNotify();

--7.Attivare tutti i corsi non ancora attivi.
-- Che cosa succede questa volta e perché? Quante tuple sono state aggiornate?

UPDATE corsi
SET attivato = true
WHERE attivato = false;

-- NOTICE:  A professor cannot be assigned to more than five active courses.
-- UPDATE 4

-- il trigger ha fatto il controllo la tupla che ha violato il vincolo non è stata modificata,
-- ma le altre 4 tuple che superavano il controllo sono state modificate

/*
8.Provare a creare nuovamente uno dei due trigger ControllaProf 
creati in precedenza con comportamento analogo ed esecuzione orientata 
alla tupla ma di tipo AFTER se prima era BEFORE e viceversa.
*/

CREATE OR REPLACE FUNCTION ControllaProf() RETURNS TRIGGER AS $$
DECLARE
    active_courses_count INT;
BEGIN
    IF NEW.attivato THEN
        SELECT COUNT(*) INTO active_courses_count
        FROM corsi
        WHERE professore = NEW.professore AND attivato = true;

        IF active_courses_count > 5 THEN
            ROLLBACK;
            RAISE EXCEPTION 'A professor cannot be assigned to more than five active courses.';
        END IF;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ControllaProf
AFTER INSERT OR UPDATE ON corsi
FOR EACH ROW EXECUTE PROCEDURE ControllaProf();

-- modifica il trigger, mettendo AFTER al posto di BEFORE e mettendo ROLLBACK prima dell'eccezione,
--e rimuovendo il RETURN NULL per indicare che la modifica va bene

/*
9.Provare a creare nuovamente uno dei due trigger ControllaProf 
creati in precedenza con comportamento analogo ma esecuzione orientata all'insieme.
*/

CREATE OR REPLACE FUNCTION ControllaProf() RETURNS TRIGGER AS $$
DECLARE
    prof_EXCEPTION RECORD;
BEGIN
    SELECT professore INTO prof_EXCEPTION
    FROM corsi
    WHERE attivato = true
    GROUP BY professore
    HAVING COUNT(*) > 5;

    IF FOUND THEN
        ROLLBACK;
        RAISE EXCEPTION 'A professor cannot be assigned to more than five active courses: %', prof_EXCEPTION.professore;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ControllaProf
AFTER INSERT OR UPDATE ON corsi
FOR EACH STATEMENT EXECUTE PROCEDURE ControllaProf();