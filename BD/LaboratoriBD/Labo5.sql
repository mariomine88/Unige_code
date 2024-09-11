/*
Laboratorio 5, Eugenio Vassallo, Mario Madalin Biberia, Umeshan Panchabalasingham

0:info pg_class:
SELECT 
    c.oid,
    c.relname,
    c.relfilenode,
    c.relam,
    c.relpages,
    c.relhasindex,
    c.relkind,
    pg_total_relation_size(c.oid) AS total_size_bytes,
    s.n_tup_ins AS num_tuples_inserted,
    s.n_tup_upd AS num_tuples_updated,
    s.n_tup_del AS num_tuples_deleted,
    s.n_live_tup AS num_tuples_live,
    s.n_dead_tup AS num_tuples_dead
FROM 
    pg_namespace n 
    JOIN pg_class c ON n.oid = c.relnamespace
    LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
WHERE 
    n.nspname = 'unicorsilarge'
    AND c.relkind = 'r'  -- Consider only ordinary tables
ORDER BY 
    c.relname;
(comando trovato su internet, non ho capito come trovare queste informazioni con i comandi del labo3)

1 numero di blocchi utilizzati per memorizzare le tabelle e gli indici: "num_tuples_live"
2 numero di tuple contenute in ciascuna tabella: "relpages"
"relname"	"relpages"	"num_tuples_live"
"corsi"	        17	        2000
"corsidilaurea"	0	        23
"esami"	        13	        1674
"pianidistudio"	0	        0
"professori"	15	        2000
"studenti"	    715	        60000


1:Considerare l'interrogazione per determinare tutti gli esami.
-SELECT * FROM esami;
Visualizzare il piano di esecuzione fisico scelto dal sistema usando prima la modalità testuale e poi quella grafica (di interpretazione più immediata).
Il piano include un singolo nodo.
Quale cammino di accesso alla relazione esami è stato utilizzato?
-Scansione Sequenziale (Seq Scan)
Quale operatore fisico viene utilizzato ?
-Seq Scan
Qual è il costo stimato per il nodo?
-00.00
Qual è la dimensione stimata per il risultato? Qual è la dimensione effettiva? Ci sono differenze tra questi due valori?
-105, 105, in teoria si, se il database viene aggiornato è possibile che le righe attese non coincidano con quelle effettive
Qual è il tempo di esecuzione complessivo del piano?
-0.069ms
Provare adesso a rieseguire l'interrogazione più volte. Quali valori cambiano? Come mai?
-cambia di pochissimo il tempo di esecuzione perchè dipende dall'hardware del pc
(*) Provate infine a mappare il piano di esecuzione fisico scelto da Postgres nella notazione proposta in aula (usate carta e penna e, se volete caricare la soluzione, fate una foto).

2:Considerare adesso 'interrogazione per determinare tutti gli esami con voto superiore a 18.
-SELECT * FROM ESAMI WHERE voto > 18;
Visualizzare il piano di esecuzione fisico scelto dal sistema usando prima la modalità testuale e poi quella grafica.
(*) Provare a rappresentare il piano logico ottimizzato corrispondente. Il piano logico contiene più o meno nodi rispetto al piano fisico?
Il piano fisico individuato dal sistema è diverso da quello descritto al punto (1)? (osservate solo quanto restituito dal sistema) 
-no
Quale cammino di accesso alla relazione esami è stato utilizzato?
-Scansione Sequenziale (Seq Scan)
Quale operatore fisico viene utilizzato? E' uguale o diverso rispetto a quello individuato al punto (1)?
--Seq Scan, uguale
Qual è il costo stimato per il nodo?
-0.00
Qual è la dimensione stimata per il risultato? Qual è la dimensione effettiva? Ci sono differenze tra questi due valori?
80,80, teoricamente si ma se il database non cambia non ci dovrebbero essere differenze
Qual è il tempo di esecuzione complessivo del piano?
-0.094ms
(*) Provate infine a mappare il piano di esecuzione fisico scelto da Postgres nella notazione proposta in aula (usate carta e penna e, se volete caricare la soluzione, fate una foto).

3:Creare un indice ad albero non clusterizzato sull'attributo voto della tabella esami.
-CREATE INDEX indicealberoNC on unicorsi.esami (voto)
Individuare nuovamente il piano di esecuzione scelto dal sistema per determinare tutti gli esami con voto superiore a 18.
-SELECT * FROM ESAMI WHERE voto > 18;
(*) Provare a rappresentare il piano logico ottimizzato corrispondente. E' diverso da quello descritto al punto (2)? Il piano logico contiene più o meno nodi rispetto al piano fisico?
Il piano fisico individuato dal sistema è diverso da quello descritto al punto (2)? (osservate solo quanto restituito dal sistema)
-no
Quale cammino di accesso alla relazione esami è stato utilizzato? 
-sequential scan
Quale operatore fisico viene utilizzato ?
-seq scan
Qual è il costo stimato per il nodo?
0.00
Qual è la dimensione stimata per il risultato? Qual è la dimensione effettiva? Ci sono differenze tra questi due valori?
80,80, teoricamente si ma se il database non cambia non ci dovrebbero essere differenze
Qual è il tempo di esecuzione complessivo del piano?
0.087mss
(*) Provate infine a mappare il piano di esecuzione fisico scelto da Postgres nella notazione proposta in aula (usate carta e penna e, se volete caricare la soluzione, fate una foto).

4:Individuare adesso il piano di esecuzione scelto dal sistema per determinare tutti gli esami con voto superiore a 29.
(*) Provare a rappresentare il piano logico ottimizzato corrispondente. E' diverso da quello descritto al punto (3)?
Il piano fisico individuato dal sistema è diverso da quello descritto al punto (3)? (osservate solo quanto restituito dal sistema)
-no
Quale cammino di accesso alla relazione esami è stato utilizzato?
-sequential scan
Quanti nodi contiene adesso il piano? (*) Il piano logico contiene più o meno nodi rispetto al piano fisico?
-1 nodo
Quali operatori fisici vengono utilizzati? (vedere la documentazione resa disponibile sugli operatori fisici in PostgreSQL)
-seq scan
Qual è la dimensione stimata per il risultato? Qual è la dimensione effettiva? Ci sono differenze tra questi due valori?
7,8, si
Qual è il tempo di esecuzione complessivo del piano?
0.049ms
(*) Provate infine a mappare il piano di esecuzione fisico scelto da Postgres nella notazione proposta in aula, estendendola se necessario, utilizzando la documentazione resa disponibile sugli operatori fisici in PostgreSQL (usate carta e penna e, se volete caricare la soluzione, fate una foto).

5:Clusterizzare la tabella esami rispetto all'indice ordinato su voto creato in precedenza ed eseguire il comando ANALYZE per aggiornare statistiche.
-CLUSTER unicorsi.esami using indicealberoNC
Individuare nuovamente  il piano di esecuzione scelto dal sistema per determinare tutti gli esami con voto superiore a 29.
Il piano fisico individuato dal sistema è diverso da quello descritto al punto (4)? (osservate solo quanto restituito dal sistema)
-no
Quale cammino di accesso alla relazione esami è stato utilizzato?
Sequentiual scan
Quanti nodi contiene il piano? 
-8
Quali operatori fisici vengono utilizzati? (vedere la documentazione resa disponibile sugli operatori fisici in PostgreSQL)
Seq Scan
Qual è la dimensione stimata per il risultato? Qual è la dimensione effettiva? Ci sono differenze tra questi due valori?
7,8
Qual è il tempo di esecuzione complessivo del piano?
0.032ms 
(*) Provate infine a mappare il piano di esecuzione fisico scelto da Postgres nella notazione proposta in aula, estendendola se necessario, utilizzando la documentazione resa disponibile sugli operatori fisici in PostgreSQL (usate carta e penna e, se volete caricare la soluzione, fate una foto).

6:Individuare il piano di esecuzione scelto dal sistema per determinare tutti gli esami con voto superiore a 29 sostenuti dopo il 2018-05-01.
EXPLAIN ANALYZE
SELECT *
FROM unicorsi.esami
WHERE voto > 29 and data > '2018-05-01'
Il piano fisico individuato dal sistema è diverso da quello descritto al punto (5)? (osservate solo quanto restituito dal sistema)
-no
Quale cammino di accesso alla relazione esami è stato utilizzato?
-sequential scan
Quanti nodi contiene il piano?
0
Quali operatori fisici vengono utilizzati? (vedere la documentazione resa disponibile sugli operatori fisici in PostgreSQL)
-seq scan
Qual è la dimensione stimata per il risultato? Qual è la dimensione effettiva? Ci sono differenze tra questi due valori?
1,0
Qual è il tempo di esecuzione complessivo del piano?
0.034ms
(*) Provate infine a mappare il piano di esecuzione fisico scelto da Postgres nella notazione proposta in aula, estendendola se necessario, utilizzando la documentazione resa disponibile sugli operatori fisici in PostgreSQL (usate carta e penna e, se volete caricare la soluzione, fate una foto).

7:Creare un indice ad albero non clusterizzato sull'attributo data di esami.
-CREATE INDEX alberodataesamiNC on unicorsi.esami(data)
Individuare il piano di esecuzione scelto dal sistema per determinare tutti gli esami con voto superiore a 29 sostenuti dopo il 2020-04-28.
-Sequential scan
Il piano fisico individuato dal sistema è diverso da quello descritto al punto (6)? (osservate solo quanto restituito dal sistema)
-no
Quale cammino di accesso alla relazione esami è stato utilizzato?
-Sequential scan
Quanti nodi contiene il piano?
-1
Quali operatori fisici vengono utilizzati? (vedere la documentazione resa disponibile sugli operatori fisici in PostgreSQL)
Seq scan
Le condizioni su cui sono stati utilizzati gli indici sono fattori booleani?
-si
Qual è la dimensione stimata per il risultato? Qual è la dimensione effettiva? Ci sono differenze tra questi due valori?
1,0
Qual è il tempo di esecuzione complessivo del piano?
-0.031
(*) Provate infine a mappare il piano di esecuzione fisico scelto da Postgres nella notazione proposta in aula, estendendola se necessario, utilizzando la documentazione resa disponibile sugli operatori fisici in PostgreSQL (usate carta e penna e, se volete caricare la soluzione, fate una foto).

8:Creare un indice ordinato sull'attributo matricola della tabella studenti e sull'attributo studente di esami.
-CREATE INDEX matricolastudentiNC on unicorsi.studenti(matricola);
-CREATE INDEX studentiesamiNC on unicorsi.esami(studente);
Individuare il piano di esecuzione scelto dal sistema per determinare il risultato del join tra le tabelle esami e studenti.
-SELECT * FROM unicorsi.studenti,unicorsi.esami
-Nested loop
(*) Provare a rappresentare il piano logico ottimizzato corrispondente.
Quali cammini di accesso alle relazioni studenti ed esami sono stati utilizzati?
-Seq scan on esami, seq scan on studenti 
Quanti nodi contiene il piano? (*) Il piano logico contiene più o meno nodi rispetto al piano fisico? Cosa vuol dire?
-4
Quali operatori fisici vengono utilizzati? (vedere la documentazione resa disponibile sugli operatori fisici in PostgreSQL)
-Nested loop, seq scan, materialize
Quale algoritmo (operatore fisico) è stato scelto per realizzare (=implementare) l'operatore logico di join?
-Nested loop
Qual è la relazione outer?
-seq scan
Qual è la dimensione stimata per il risultato? Qual è la dimensione effettiva? Ci sono differenze tra questi due valori?
-6720,6720,no
Qual è il tempo di esecuzione complessivo del piano?
-1,625ms

9:Individuare il piano di esecuzione scelto dal sistema per determinare il risultato del join tra le tabelle esami e studenti, ristretto agli esami con voto maggiore di 29.
SELECT *
FROM unicorsi.studenti,unicorsi.esami
WHERE voto > 29
-Nested loop
(*) Provare a rappresentare il piano logico ottimizzato corrispondente.
Quali cammini di accesso alle relazioni studenti ed esami sono stati utilizzati?
Seq scan on studenti, seq scan on esami
Quanti nodi contiene il piano? (*) Il piano logico contiene più o meno nodi rispetto al piano fisico?
4
Quali operatori fisici vengono utilizzati? (vedere la documentazione resa disponibile sugli operatori fisici in PostgreSQL)
Nested loop, seq scan, materialize
Quale algoritmo (operatore fisico) è stato scelto per realizzare (=implementare) l'operatore logico di join?
Nested loop
Qual è la relazione outer?
seq scan
Qual è la dimensione stimata per il risultato? Qual è la dimensione effettiva? Ci sono differenze tra questi due valori?
7,8, si
Qual è il tempo di esecuzione complessivo del piano?
0.189ms

10:Clusterizzare la tabella esami rispetto a studente e la tabella studenti rispetto a matricola (ed eseguite ANALYZE per aggiornare cataloghi).
-CLUSTER unicorsi.studenti using matricolastudentiNC;
-CLUSTER unicorsi.esami using studentiesamiNC;
Individuare il piano di esecuzione scelto dal sistema per determinare il risultato del join tra le tabelle esami e studenti
-Nested loop
(*) Provare a rappresentare il piano logico ottimizzato corrispondente.
Quali cammini di accesso alle relazioni studenti ed esami sono stati utilizzati?
-Seq scan on studenti, seq scan on esami
Quanti nodi contiene il piano? (*) Il piano logico contiene più o meno nodi rispetto al piano fisico?
4
Quali operatori fisici vengono utilizzati? (vedere la documentazione resa disponibile sugli operatori fisici in PostgreSQL)
seq scan, nested loop, materialize
Quale algoritmo (operatore fisico) è stato scelto per realizzare (=implementare) l'operatore logico di join?
nested loop
Qual è la relazione outer?
seq scan
Qual è la dimensione stimata per il risultato? Qual è la dimensione effettiva? Ci sono differenze tra questi due valori?
64,64,no
Qual è il tempo di esecuzione complessivo del piano?
1.804ms
Provate adesso a modificare la richiesta, restringendo il risultato alle sole tuple con con voto maggiore di 29.
Come cambia il piano rispetto al precedente?
-il numero di tuple restituite è minore, quindi il tempo di esecuzione è minore
*/
