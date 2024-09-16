# Laboratorio di LPO, 1 dicembre 2023: composizione di oggetti e interfacce in Java

Il codice di partenza per questo laboratorio è disponibile nel folder `lab04`; le specifiche dei metodi di `Circle`, `Rectangle` e `AreaComparator` si trovano nelle interfacce `Shape` e `ShapeComparator`; per semplicità gli invarianti di classe non impongono limiti superiori alle dimensioni delle figure. Ogni oggetto di tipo `Shape` deve essere owner esclusivo del punto sul piano cartesiano che rappresenta il suo centro geometrico. 


1. Completare le classi `Circle` e `Rectangle` che implementano l'interfaccia `Shape`.

1. Completare la classe `AreaComparator` che implementa l'interfaccia `ShapeComparator`.

1. Completare la classe `Shapes` che contiene vari metodi di classe di utilità che implementano operazioni su array di figure.

1. Utilizzare la classe `ShapeTest` per verificare il corretto funzionamento del codice.

## Compilazione ed esecuzione di classi contenute in package
Le classi e interfacce di questo laboratorio sono contenute nel package `lab04`; per questo motivo i file sorgenti `.java` si trovano nel folder `lab04`. Per compilare ed eseguire la classe `ShapeTest` potete usare un IDE, oppure
da shell si possono lanciare i comandi `javac ShapeTest.java` e `java -ea lab04.ShapeTest` a partire dal folder che contiene `lab04`.

Per compilare ed eseguire la classe dal folder `lab04` bisogna usare l'opzione `-cp` (classpath): `javac -cp .. ShapeTest.java` e `java -cp .. -ea lab04.ShapeTest`. 

 
	

