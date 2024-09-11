--Laboratorio 3 prima parte, Eugenio Vassallo, Mario Madalin Biberia, Umeshan Panchabalasingham

--FUNZIONI OUTER JOIN
--1 l’elenco in ordine alfabetico (per denominazione) dei corsi, con eventuale nominativo del professore titolare
SELECT corsi.denominazione,professori.nome, professori.cognome 
FROM unicorsi.corsi
LEFT OUTER JOIN unicorsi.professori on corsi.professore = professori.id
ORDER BY corsi.denominazione ASC

--2 l’elenco alfabetico degli studenti iscritti a matematica, con l’eventuale relatore che li segue per la tesi
SELECT DISTINCT studenti.cognome, studenti.nome, professori.cognome as Relatore
FROM unicorsi.studenti
LEFT OUTER JOIN unicorsi.professori on studenti.relatore = professori.id
JOIN unicorsi.corsidilaurea 
on studenti.corsodilaurea = (SELECT corsidilaurea.id FROM unicorsi.corsidilaurea WHERE corsidilaurea.denominazione = 'Matematica')
ORDER BY studenti.cognome ASC, studenti.nome ASC

--FUNZIONI DI GRUPPO
--1 la votazione minima, media e massima conseguita nei corsi del corso di laurea in informatica;
SELECT MIN(esami.voto) as MIN, AVG(esami.voto) as AVG, MAX(esami.voto) as MAX
FROM unicorsi.esami, unicorsi.corsi
WHERE corsi.denominazione = 'Informatica'

--2 i nominativi, in ordine alfabetico, dei professori titolari di più di due corsi attivati (attributo Attivato in Corsi), con l’indicazione di quanti corsi tengono;
SELECT professori.cognome, professori.nome, COUNT(corsi.id) as numero_corsi
FROM unicorsi.professori
JOIN unicorsi.corsi on professori.id = corsi.professore 
WHERE corsi.attivato = true --controlla se il corso è attivato
GROUP BY professori.nome, professori.cognome
HAVING COUNT(corsi.id) > 2 --elimina i professori con un solo corso
ORDER BY professori.cognome ASC, professori.nome ASC

--3 l’elenco, in ordine alfabetico, dei professori con l’indicazione del numero di studenti di cui sono relatori [(*) indicando 0 se non seguono alcuno studente per la tesi];
SELECT professori.cognome, professori.nome, COUNT(studenti.relatore) as num_studenti
FROM unicorsi.professori
JOIN unicorsi.studenti on professori.id = studenti.relatore
GROUP BY professori.cognome, professori.nome
ORDER BY professori.cognome ASC, professori.nome ASC

--3* l’elenco, in ordine alfabetico, dei professori con l’indicazione del numero di studenti di cui sono relatori [(*) indicando 0 se non seguono alcuno studente per la tesi];
SELECT professori.cognome, professori.nome, COUNT(studenti.relatore) as num_studenti
FROM unicorsi.professori
LEFT OUTER JOIN unicorsi.studenti on professori.id = studenti.relatore
GROUP BY professori.cognome, professori.nome
ORDER BY professori.cognome ASC, professori.nome ASC

--4 la matricola degli studenti iscritti al corso di studi in informatica che hanno registrato (almeno) due voti per corsi diversi nello stesso mese, con la media dei voti riportati
--la matricola degli studenti iscritti al corso di studi in informatica che hanno registrato (almeno) due voti per corsi diversi nello stesso mese, con la media dei voti riportati 
SELECT studenti.matricola,EXTRACT(YEAR FROM esami.data)as anno, EXTRACT(MONTH FROM esami.data)as mese, AVG(esami.voto) as media_voti
FROM unicorsi.studenti
JOIN unicorsi.corsidilaurea 
	on studenti.corsodilaurea = corsidilaurea.id
LEFT OUTER JOIN unicorsi.esami on studenti.matricola = esami.studente
WHERE corsidilaurea.denominazione = 'Informatica' --filtro per trovare solo gli studenti di informatica
GROUP BY studenti.matricola, EXTRACT (YEAR FROM esami.data), EXTRACT(MONTH FROM esami.data)
HAVING COUNT(DISTINCT esami.corso) >= 2;

--SOTTOINTERROGAZIONI SEMPLICI
--1  l’elenco dei corsi di laurea che nell’A.A. 2010/2011 hanno meno iscritti di quelli che si sono avuti ad informatica nello stesso A.A. 
SELECT corsidilaurea.denominazione
FROM unicorsi.corsidilaurea
JOIN unicorsi.studenti on studenti.corsodilaurea = corsidilaurea.id
WHERE studenti.iscrizione = 2010
GROUP BY corsidilaurea.denominazione
HAVING COUNT(studenti.matricola) < (
	SELECT COUNT(studenti.matricola)
	FROM unicorsi.studenti
	JOIN unicorsi.corsidilaurea on studenti.corsodilaurea = corsidilaurea.id
	WHERE corsidilaurea.denominazione = 'Informatica' AND studenti.iscrizione = 2010)

--2 la matricola dello studente di informatica che ha conseguito la votazione più alta
SELECT DISTINCT studenti.matricola
FROM unicorsi.studenti
JOIN unicorsi.corsidilaurea on studenti.corsodilaurea = corsidilaurea.id
JOIN unicorsi.esami on studenti.matricola = esami.studente
WHERE corsidilaurea.denominazione = 'Informatica' 
	AND esami.voto = (SELECT MAX(esami.voto) --subquery per trovare gli studenti con il voto massimo
					 FROM unicorsi.esami
					 WHERE esami.studente IN 
					  (SELECT DISTINCT studenti.matricola
						FROM unicorsi.studenti
						JOIN unicorsi.corsidilaurea on studenti.corsodilaurea = corsidilaurea.id
						WHERE corsidilaurea.denominazione = 'Informatica')
					  )



