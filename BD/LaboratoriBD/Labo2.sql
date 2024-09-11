--Query labo2 Eugenio Vassallo, Mario Madalin Biberia, Umeshan Panchabalasingham
--query singola relazione 1,2,3:

--la matricola e i nominativi degli studenti iscritti prima dell’A.A. 2007/2008 che non sono ancora in tesi (non hanno assegnato nessun relatore);
SELECT studenti.matricola, studenti.nome, studenti.cognome
FROM studenti
WHERE studenti.iscrizione < '2007' AND studenti.relatore IS NULL;

--l’elenco dei corsi di laurea, in ordine alfabetico per facoltà e denominazione del corso di laurea, attivati prima dell’A.A. 2006/2007 (escluso) e dopo l’A.A. 2009/2010 (escluso);
SELECT corsidilaurea.facolta, corsidilaurea.denominazione
FROM unicorsi.corsidilaurea
WHERE corsidilaurea.attivazione < '2006' OR corsidilaurea.attivazione > '2009'
ORDER BY corsidilaurea.facolta ASC, corsidilaurea.denominazione ASC

--la matricola e i nominativi, in ordine di matricola inverso, degli studenti il cui cognome non è ‘Serra’, ‘Melogno’ né ‘Giunchi’ oppure risiedono in una città tra Genova, La Spezia e Savona.
SELECT studenti.matricola, studenti.nome, studenti.cognome
FROM unicorsi.studenti
WHERE studenti.cognome NOT IN ('Serra','Melogno','Giunchi') 
	OR studenti.residenza IN ('Genova','La Spezia','Savona')
ORDER BY studenti.matricola DESC

--query a più relazioni 4,5,6:
--la matricola degli studenti laureatisi in informatica prima del novembre 2009;
SELECT studenti.matricola, studenti.nome, studenti.cognome
FROM studenti
JOIN corsidilaurea ON studenti.corsodilaurea = corsidilaurea.id
WHERE studenti.laurea < '2009-01-11' and NOT NULL;

--l’elenco in ordine alfabetico dei nominativi degli studenti, con, per ognuno, il cognome del relatore associato;
SELECT studenti.cognome,studenti.nome,professori.cognome
FROM unicorsi.studenti
JOIN professori ON studenti.relatore = professori.id
WHERE studenti.relatore IS NOT NULL
ORDER BY studenti.cognome, studenti.nome ASC

--l’elenco, senza duplicati e in ordine alfabetico inverso, degli studenti che hanno presentato il piano di studi per il quinto anno del corso di laurea di informatica nell’a.a. 2011/2012 e sono in tesi (hanno assegnato un relatore).
SELECT DISTINCT studenti.cognome, studenti.nome
from unicorsi.studenti
JOIN unicorsi.pianidistudio on studenti.matricola = pianidistudio.studente
WHERE pianidistudio.anno = 5
AND studenti.corsodilaurea = (SELECT id from unicorsi.corsidilaurea WHERE corsidilaurea.denominazione = 'Informatica')
AND pianidistudio.annoaccademico = 2011
AND studenti.relatore is not null
ORDER by studenti.cognome DESC, studenti.nome DESC

--query insiemistiche 7,8,9:
--cognome, nome e qualifica (’studente’/’professore’) di studenti e professori. [Una interrogazione può restituire un valore costante, basta includere tale valore nella clausola SELECT.]
SELECT studenti.cognome, studenti.nome, 'studente'
FROM unicorsi.studenti
UNION
SELECT professori.cognome, professori.nome, 'professore'
FROM unicorsi.professori

--gli studenti di informatica che hanno passato basi di dati 1 ma non interfacce grafiche nel giugno del 2010.
SELECT studenti.matricola, studenti.nome, studenti.cognome
FROM unicorsi.studenti
JOIN unicorsi.esami on studenti.matricola = esami.studente --combina le righe di studenti e esami dove matricola = esami.studente
JOIN unicorsi.corsi on esami.corso = corsi.id -- combina le righe di esami e corsi dove l'id del corso è lo stesso del corso associato all'esame
WHERE corsi.denominazione = 'Basi Di Dati 1'
AND esami.data >= '2010-06-01' and esami.data <= '2010-06-30' --hanno passato Basi di dati a giugno (fra l'1 e il 30 compresi)
AND studenti.corsodilaurea = (SELECT id from unicorsi.corsidilaurea where corsidilaurea.denominazione = 'Informatica') --gli studenti sono di informatica
    --ora bisogna specificare che NON vogliamo quelli che hanno passato interfacce grafiche sempre a giugno del 2010, quindi dobbiamo escluderli
EXCEPT 
SELECT studenti.matricola, studenti.nome, studenti.cognome
FROM unicorsi.studenti
JOIN unicorsi.esami on studenti.matricola = esami.studente 
JOIN unicorsi.corsi on esami.corso = corsi.id 
WHERE corsi.denominazione = 'Interfacce Grafiche' --cambia solo questo
AND esami.data >= '2010-06-01' and esami.data <= '2010-06-30'
AND studenti.corsodilaurea = (SELECT id from unicorsi.corsidilaurea where corsidilaurea.denominazione = 'Informatica')

--gli studenti di informatica che hanno passato basi di dati 1 ma non interfacce grafiche nel giugno del 2010.
SELECT studenti.matricola, studenti.nome, studenti.cognome
FROM unicorsi.studenti
JOIN unicorsi.esami on studenti.matricola = esami.studente --combina le righe di studenti e esami dove matricola = esami.studente
JOIN unicorsi.corsi on esami.corso = corsi.id -- combina le righe di esami e corsi dove l'id del corso è lo stesso del corso associato all'esame
WHERE corsi.denominazione = 'Basi Di Dati 1'
AND esami.data >= '2010-06-01' and esami.data <= '2010-06-30' --hanno passato Basi di dati a giugno (fra l'1 e il 30 compresi)
AND studenti.corsodilaurea = (SELECT id from unicorsi.corsidilaurea where corsidilaurea.denominazione = 'Informatica') --gli studenti sono di informatica
INTERSECT --prende solo quelli che trova del primo AND del secondo select(?)
SELECT studenti.matricola, studenti.nome, studenti.cognome
FROM unicorsi.studenti
JOIN unicorsi.esami on studenti.matricola = esami.studente 
JOIN unicorsi.corsi on esami.corso = corsi.id 
WHERE corsi.denominazione = 'Interfacce Grafiche' 
AND esami.data >= '2010-06-01' and esami.data <= '2010-06-30' --hanno passato interfacce grafiche a giugno
AND studenti.corsodilaurea = (SELECT id from unicorsi.corsidilaurea where corsidilaurea.denominazione = 'Informatica')