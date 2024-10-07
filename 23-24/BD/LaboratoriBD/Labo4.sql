--Laboratorio 4 SQL Eugenio Vassallo, Mario Madalin Biberia, Umeshan Panchabalasingham

/*
1.(*) [questa interrogazione corrisponde a un'interrogazione già 
formulata in esercitazioni precedenti (con INTERSECT e IN), la richiesta 
è ora di formularla  IN DUE DIVERSI MODI: usando EXISTS e una sotto-interrogazione 
correlata E senza usare sotto-interrogazioni ma usando due alias sulle relazioni] 
la matricola degli studenti di informatica che nel mese di giugno 2010 hanno 
registrato voti sia per il corso di basi di dati 1 che per quello di interfacce grafiche
*/

--USING EXISTS
SELECT studenti.matricola
FROM studenti
WHERE EXISTS (
    SELECT 1
    FROM esami 
    WHERE esami.studente = studenti.matricola
    AND esami.corso = 'bdd1n'
	AND EXTRACT(MONTH FROM esami.data) = 6
    AND EXTRACT(YEAR FROM esami.data) = 2010
) AND EXISTS (
    SELECT 1
	FROM esami 
    WHERE esami.studente = studenti.matricola
    AND esami.corso = 'ig'
    AND EXTRACT(MONTH FROM esami.data) = 6
    AND EXTRACT(YEAR FROM esami.data) = 2010
);

SELECT DISTINCT s1.matricola
FROM studenti s1
JOIN esami e1 ON s1.matricola = e1.studente
JOIN esami e2 ON s1.matricola = e2.studente
WHERE e1.corso = 'bdd1n'
AND e2.corso = 'ig'
AND EXTRACT(MONTH FROM e1.data) = 6
AND EXTRACT(YEAR FROM e1.data) = 2010
AND EXTRACT(MONTH FROM e2.data) = 6
AND EXTRACT(YEAR FROM e2.data) = 2010;

--2 la matricola degli studenti di informatica che hanno sostenuto basi di dati 1 
-- con votazione superiore alla votazione media (per tale esame);
SELECT DISTINCT studenti.matricola as studente
FROM unicorsi.studenti
JOIN unicorsi.corsidilaurea on studenti.corsodilaurea = corsidilaurea.id
JOIN unicorsi.esami on studenti.matricola = esami.studente 
JOIN unicorsi.corsi on esami.corso = corsi.id
WHERE corsidilaurea.denominazione = 'Informatica'
AND corsi.denominazione = 'Basi Di Dati 1'
AND esami.voto > (SELECT AVG(esami.voto) FROM unicorsi.esami WHERE esami.corso = 'bdd1n');

--3 i nominativi dei professori che insegnano nel maggior numero di corsi;
--[nota: non è possibile annidare funzioni di gruppo (es. MAX(COUNT)), ma si può usare  >= ALL invece di MAX]
SELECT professori.cognome, professori.nome, COUNT(*) as numerocorsi
FROM unicorsi.professori
JOIN unicorsi.corsi on corsi.professore = professori.id
GROUP BY professori.cognome, professori.nome
HAVING COUNT (*) >= ALL
(SELECT COUNT (*) 
 FROM unicorsi.corsi 
 GROUP BY Professore)

--4 i professori che sono titolari dei corsi i cui voti medi sono i più  alti; 
SELECT professori.nome, professori.cognome, AVG(esami.voto) as media
FROM unicorsi.professori
JOIN unicorsi.corsi on professori.id = corsi.professore
JOIN unicorsi.esami on corsi.id = esami.corso
GROUP BY professori.nome, professori.cognome
ORDER BY media DESC
LIMIT 1
--(il risultato è diverso da quello atteso ma la media più alta è 26 ed appartiene a michele levrero non a claudio bettini)

--5per ogni corso, la matricola degli studenti che hanno ottenuto un voto 
--sotto la votazione media del corso, indicando anche corso e voto;
SELECT esami.corso, studenti.matricola as studente, esami.voto
FROM unicorsi.studenti
JOIN unicorsi.esami on studenti.matricola = esami.studente
JOIN unicorsi.corsi on esami.corso = corsi.id
WHERE esami.voto < (SELECT AVG(esami1.voto)
	FROM unicorsi.esami as esami1 --importante l'alias per evitare ambiguità!!
    WHERE esami1.corso = esami.corso
	)

--6media più alta fra tutti gli studenti sotto un relatore
SELECT p.nome as Nomeprof, p.cognome as cognprof, s.nome,s.cognome
FROM studenti as s
JOIN professori as p on s.relatore = p.id
WHERE ( select max(media) from studenti
		join(select studente,avg(voto) as media 
			from esami
			join studenti on matricola = studente and relatore IS NOT NULL
			group by studente)
 		on matricola = studente
	  	where relatore =s.relatore)
		= 
		(select avg(voto) FROM esami
		 WHERE studente=s.matricola)

/*
7.per ogni docente, i corsi correntemente attivati in cui ha attribuito 
una votazione media superiore alla votazione
 media assegnata da tale docente (indipendentemente dal corso);
*/
SELECT nome,cognome, X.id 
FROM corsi X
JOIN professori on professori.id = professore 
AND attivato = true
AND (SELECT AVG(voto) from corsi
	JOIN esami on id=corso and attivato=true
	WHERE professore = X.professore)>(SELECT AVG(voto) as mediaCorso
										FROM esami
										WHERE corso=X.id)


--8.(*)gli studenti non ancora in tesi che hanno passato tutti gli esami del proprio corso di laurea.
SELECT matricola,COUNT(DISTINCT corso) 
FROM studenti X 
JOIN esami ON matricola = studente
WHERE relatore is NULL 
GROUP BY matricola
HAVING COUNT(DISTINCT corso) = (SELECT COUNT(corsodilaurea) FROM corsi
                              WHERE corsodilaurea=x.corsodilaurea
)

