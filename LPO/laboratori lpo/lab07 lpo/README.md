# Laboratorio di LPO, 4 aprile 2024

## Uso di dizionari e tabelle di hash, gestione input/output ed eccezioni 

### Esercizi proposti

1.
   Completare  il metodo `equals(boolean)` affinché due oggetti di `Person` siano uguali se e solo se hanno lo stesso `id`.
   Ridefinire di conseguenza il metodo `hashCode()`.

   Completare il metodo `toString()` come specificato nel file.
   
1.
   Completare il metodo `sumScoresGroupById(Readable readable, Map<Person, Integer> output)` della classe `CsvUtilitiesClass`
   che legge dallo stream `readable` una tabella in formato CSV  con colonne `name` e `surname` di tipo `String`, `id` di tipo `long` non negativo e
   `score` di tipo `int`; converte in maiuscole `name` e `surname`, raggruppa tutte le persone con lo stesso `id`, ne calcola la somma degli `score` e salva il risultato nel dizionario `output`
   che associa a chiavi di tipo `Person` il loro `score` di tipo `Integer`.

   Dato che `output` potrebbe fare riferimento a un dizionario implementato con
   `HashMap`, è fondamentale che il punto 1 sia stato completato correttamente per assicurare l'assenza di possibili errori.
   
   Per semplicità assumere che la tabella non abbia intestazione.
   
   Per esempio, se `output` fa riferimento a un dizionario vuoto e `readable` contiene la tabella
   ```
   MARIO,ROSSI,1234,-3
   GIOVANNA,BIANCHI,4321,0
   MARIO,ROSSI,1234,5
   ```
   allora dopo la chiamata del metodo `sumScoresGroupById`, `output` farà riferimento al dizionario che associa alla persona `MARIO ROSSI` con `id 1234` lo `score 2` e alla persona `GIOVANNA BIANCHI`
   con `id 4321` lo `score 0`.

   Il metodo usa un oggetto di tipo `Scanner` per leggere la tabella e un oggetto `output` di tipo `Map<Person,Integer>` per memorizzarla e
   modificarla.  
   
   Per semplicità assumere che non ci siano inconsistenze nei dati, ossia non esistano persone con stesso `id` ma nome o cognome diverso.

   Poiché `name` e `surname` vengono convertiti in maiuscole, la tabella
   ```
   Mario,Rossi,1234,-3
   giovanna,bianchi,4321,0
   MARIO,ROSSI,1234,5
   ```
   genera lo stesso dizionario dell'esempio precedente.

1.
   Completare il metodo `<K, V> void print(Map<K, V> map, PrintWriter pw)` della classe `CsvUtilitiesClass` che permette di stampare la tabella corrispondente al dizionario `map`.
   Vengono generate tutte le colonne per i campi sia delle chiavi, sia dei valori, come definito nei corrispondenti metodi `toString()`.
   È quindi importante che tale metodo sia ridefinito correttamente in `Person` come richiesto nel punto 1.
   I campi della chiave vengono stampati prima di quelli dei valori.
   
   Nel caso del dizionario modificato dal metodo `sumScoresGroupById` dell'esempio precedente, verrebbe stampato
   ```
   MARIO,ROSSI,1234,2
   GIOVANNA,BIANCHI,4321,0
   ```  


1.
   Completare il metodo `int compare(Person p1, Person p2)` della classe `ComparePersonBySurname`
   che implementa l'interfaccia `Comparator<Person>`.
   Il metodo ordina per cognome (ordine naturale di `String` su `surname`) oggetti di `Person`; in caso di stesso cognome viene considerato
   l'ordinamento naturale su `id`.  Viene restituito un numero negativo se `p1` viene prima di `p2`, positivo se `p1` viene dopo `p2`,
   0 se `p1.equals(p2)`.  

   Un oggetto di tipo `ComparePersonBySurname` permette di ordinare per cognome le chiavi di tipo `Person` in dizionari implementati con
   alberi red-black dalla classe  `TreeMap<K,V>` (vedere il punto 6).

1.
   Completare i metodi `tryOpenInput(String inputPath)` e `tryOpenOutput(String outputPath)` della classe `Main`,
   come specificato nel file.

1.
   Completare il metodo `main(String[] args)`della classe `Main` come specificato nel body.
   La classe implementa una semplice interfaccia da linea di comando con le opzioni
   ```
	-i <input>
	-o <output>
	-sort
   ```
   L'opzione `-i <input>` definisce il file di testo di input, l'opzione `-o <output>` quello di output, l'opzione `-sort` richiede che le righe
   della tabella di output siano stampate con le chiavi ordinate rispetto all'ordine definito al punto 4, usando un oggetto di `TreeMap`.
   Una stessa opzione può essere ripetuta più volte da linea di comando, l'ultima sarà quella considerata.
   Se input o output non vengono specificati, il programma interagisce rispettivamente con lo standard input o output.
   
   Esempi di esecuzione:
   ```
   $ java -cp java/labs/bin lab07.Main -i test.csv -o out.csv
   $ cat out.csv
   ```
   ```
   GIOVANNA,BIANCHI,4321,0
   MARIA PIERA,ROSSI,5777,42
   MARIO,ROSSI,1234,2
   ARIANNA,BIANCHI,2124,2
   GIACOMO,VERDI,8352,6
   ARIANNA,BIANCHI,3104,8
   ```
   ```
   $ java -cp java/labs/bin lab07.Main -i test.csv -o out-sorted.csv -sort
   $ cat out-sorted.csv
   ```
   ```
   ARIANNA,BIANCHI,2124,2
   ARIANNA,BIANCHI,3104,8
   GIOVANNA,BIANCHI,4321,0
   MARIO,ROSSI,1234,2
   MARIA PIERA,ROSSI,5777,42
   GIACOMO,VERDI,8352,6
   ```

