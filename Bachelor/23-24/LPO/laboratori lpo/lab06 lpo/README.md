# Laboratorio di LPO, 6 marzo 2023: iterator pattern

## Esercizi proposti

1.
   Completare la classe `SimpleRange` che implementa oggetti immutabili e iterabili che rappresentano intervalli di numeri interi e
   `SimpleRangeIterator` che implementa i corrispondenti iteratori.

   Conseguentemente, se `r` è un oggetto della classe `SimpleRange`,
   allora  `r.iterator()` restituisce un nuovo oggetto della classe `SimpleRangeIterator` che permette di iterare sugli elementi di `r` in ordine crescente,
   utilizzando l'enhanced-for o i metodi `hasNext()` e `next()`.

   Per esempio, `SimpleRange.withStartEnd(-1,3)` rappresenta la sequenza di interi `-1, 0, 1, 2`,  `SimpleRange.withEnd(2)` la sequenza `0, 1` e 
   `SimpleRange.withStartEnd(2,2)` o SimpleRange.withStartEnd(3,-1)` la sequenza vuota e il codice
   ```java
   for(int i : SimpleRange.withStartEnd(start,end)){...}
   ```
   è equivalente a
   ```java
   for(int i = start; i < end; i++){...}
   ```
   Utilizzare la classe <code>RangeTest</code> come base di partenza per i test.

   #### Importante
   L'implementazione deve avere una complessità spaziale **costante**, indipendente dal numero di elementi contenuti negli intervalli.
   Per esempio, la quantità di memoria utilizzata per rappresentare `SimpleRange.withEnd(1)` e `SimpleRange.withEnd(10000)` deve essere la stessa e la minima possibile.

1.
   Completare le classi `StepRange` e `StepRangeIterator`, analogamente a quanto fatto nel punto precedente.
  
   `StepRange` estende l'espressività di `Range` permettendo di definire con valori arbitrari, purché diversi da 0,
    la costante `step` che specifica la "distanza" tra un elemento dell'intervallo e quello immediatamente precedente.
    Di conseguenza, se `step > 0`, allora la sequenza dell'intervallo sarà crescente, mentre sarà decrescente se `step < 0`.
    Nel caso degli oggetti `Range` questa costante è sempre implicitamente uguale a 1.

    Per esempio, `StepRange.withStartEndStep(1, 5, 2)` rappresenta la sequenza `1, 3` e
    `StepRange.withStartEndStep(5, 1, -2)` la sequenza `5, 3`.

    Se `step>0`, il codice
    ```java
    for(int i : StepRange.withStartEndStep(start, end, step){...}
    ```
    è equivalente a
    ```java
    for(int i = start; i < end; i+=step){...}
    ```
    e se `step < 0`
    ```java
    for(int i : StepRange.withStartEndStep(start, end, step){...}
    ```
    è equivalente a
    ```java
    for(int i = start; i > end; i+=step){...}
    ```
