/*
[Routine con parametri di input e output] Creare una routine AggiornaStip,
con un parametro di input di tipo numerico soglia.

Se lo stipendio medio dei professori titolari di almeno un corso attivato 
è inferiore a un valore soglia specificato in input dall'utente, la routine 
dovrà per aumentare di 10% lo stipendio dei soli professori titolari di almeno un corso attivato.

In caso contrario, lo stipendio dei soli professori titolari
di almeno un corso attivato andrà aumentato del 5%. 

La routine dovrà restituire l’ammontare totale degli aumenti; 
scegliete voi come restituire tale valore
(usando la clausola RETURNS o come parametro di output, oppure provando entrambe le alternative). 

La routine dovrà notificare attraverso un RAISE NOTICE la percentuale di aumento applicata.
*/

CREATE OR REPLACE FUNCTION AggiornaStip(IN soglia NUMERIC(8,2), OUT total_increase NUMERIC)
LANGUAGE plpgsql
AS $$
DECLARE 
    stipendio_medio DECIMAL(8,2);
    increase_percent DECIMAL(5,2);
BEGIN
    -- calcolo la media degli stipendi dei professori
    SELECT AVG(professori.stipendio) INTO stipendio_medio
    FROM professori
    JOIN corsi ON professori.id = corsi.professore
    WHERE corsi.attivato = true;

    -- determino la percentuale di aumento
    IF stipendio_medio < soglia THEN
        increase_percent := 0.1;
    ELSE
        increase_percent := 0.05;
    END IF;

    -- calcolo l'ammontare totale degli aumenti
    SELECT SUM((stipendio * increase_percent)) INTO total_increase
    FROM professori
    JOIN corsi ON professori.id = corsi.professore
    WHERE corsi.attivato = true;

    -- incremento lo stipendio dei professori titolari di almeno un corso attivato
    UPDATE professori
    SET stipendio = stipendio * (1 + increase_percent)
    FROM corsi
    WHERE professori.id = corsi.professore AND corsi.attivato = true;

    -- notifico la percentuale di aumento applicata
    RAISE NOTICE 'The applied increase percentage is %', increase_percent * 100;
END; 
$$ LANGUAGE plpgsql;

/*
Creare una routine AggiornaStip2, con due parametri di input di tipo numerico, 
soglia e perc: soglia rappresenta un valore di stipendio di un professore,
 mentre perc rappresenta un valore percentuale. Svolgendo l'esercizio, 
 usate i cursori solo quando strettamente necessario.

Se il valore di soglia è maggiore di 1000 e la percentuale è compresa tra 0 e 100, 
la procedura visualizza il messaggio "Parametri corretti", altrimenti la procedura scrive a 
video "Parametri non corretti". 

Se i parametri in input sono corretti, 

La routine per prima cosa calcola lo stipendio medio
dei professori che sono titolari di al più un corso
(indipendentemente dal fatto che il corso sia attivato o meno).

Se tale stipendio medio è inferiore al valore soglia specificato in input,
inizialmente visualizza per ogni professore il cognome, il nome e lo scarto tra
lo stipendio e la soglia, con una opportuna nota se lo scarto è negativo.

Successivamente alla visualizzazione dei dati, aumenta del valore perc
lo stipendio di tutti professori che guadagnano meno di soglia.
*/

CREATE OR REPLACE PROCEDURE AggiornaStip2(IN soglia NUMERIC, IN perc NUMERIC)
AS $$
DECLARE 
    stipendio_medio DECIMAL;
    rec RECORD;
BEGIN
    -- controllo i parametri in input
    IF soglia > 1000 AND perc BETWEEN 0 AND 100 THEN
        RAISE NOTICE 'Parametri corretti';
    ELSE
        RAISE NOTICE 'Parametri non corretti';
        RETURN;
    END IF;

    -- calcolo la media degli stipendi dei professori titolari di al più un corso
    SELECT AVG(p.stipendio) INTO stipendio_medio
    FROM professori p
    JOIN corsi c ON p.id = c.professore
    WHERE p.id IN (
        SELECT professore 
        FROM corsi 
        GROUP BY professore 
        HAVING COUNT(*) = 1
    );

    -- se lo stipendio medio è inferiore alla soglia, visualizzo i dati e aumento lo stipendio
    IF stipendio_medio < soglia THEN
        FOR rec IN SELECT nome, cognome, stipendio - soglia AS scarto
                   FROM professori
                   WHERE stipendio < soglia
        LOOP
            RAISE NOTICE 'Professor % % has a salary difference of %', rec.nome, rec.cognome, rec.scarto;
        END LOOP;

        -- aumento lo stipendio dei professori che guadagnano meno di soglia
        UPDATE professori
        SET stipendio = stipendio * (1 + perc / 100)
        WHERE stipendio < soglia;
    END IF;
END; 
$$ LANGUAGE plpgsql;

/*
Creare una funzione datiInTab che restituisca il numero di tuple contenute
in una tabella il cui nome viene specificato in input dall’utente.
Eseguirla piu` volte con nomi di tabella diversi.
*/

CREATE OR REPLACE FUNCTION datiInTab(tableName IN text) 
RETURNS INTEGER AS $$
DECLARE 
    ilComando VARCHAR(100);
    rowCount INTEGER;
BEGIN
    ilComando := format('SELECT COUNT(*) FROM %I', tableName);
    EXECUTE ilComando INTO rowCount;
    RETURN rowCount;
END;
$$ LANGUAGE plpgsql;

SELECT datiInTab('corsi');
SELECT datiInTab('esami');
SELECT datiInTab('studenti');

/*
Creare una routine InserisciEsame1 che prende in input un valore per ogni campo 
della tabella esami ed inserisce la tupla corrispondente nella tabella, 
trasformando tutte le stringhe nel formato con lettera iniziale maiuscola 
e rimanenti caratteri minuscoli (usare a questo proposito la funzione initcap() ).
Se l’inserimento genera un errore, visualizza a video il codice dell’errore generato
associato ad un opportuno messaggio.  Considerare a questo proposito gli errori più rilevanti.
*/

CREATE OR REPLACE FUNCTION InserisciEsame1(studente VARCHAR(10), corso CHAR(10), data DATE, voto DECIMAL) 
RETURNS VOID
AS $$
BEGIN
    -- tento di inserire la tupla nella tabella
    BEGIN
        INSERT INTO Esami VALUES (studente, corso, data, voto);
    EXCEPTION WHEN others THEN
        -- in caso di errore, visualizzo il codice dell'errore generato
        RAISE NOTICE 'Error code: %, message: %', SQLSTATE, SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql;


SELECT InserisciEsame1('23glot5', 'it', '06/01/2020', 30); --success
SELECT InserisciEsame1('mario', 'it', '06/01/2020', 30); 
-- Error code: 23503, message: insert or update on table "esami" violates foreign key constraint "esami_studente_fkey"








