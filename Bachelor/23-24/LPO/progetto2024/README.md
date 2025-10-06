[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-7f7980b617ed060a017424585567c406b6ee15c891e84e1186181d67ecf80aa0.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=15037891)
# Progetto finale LPO a.a. 2023-'24
Il progetto finale consiste nell'implementazione di un'estensione del linguaggio sviluppato durante gli ultimi laboratori Java;
può quindi essere usata come base di partenza la soluzione proposta per l'ultimo laboratorio.
È comunque richiesto che le implementazioni della semantica statica e dinamica siano basate sul visitor pattern.

L'interfaccia da linea di comando per interagire con l'interprete è la stessa utilizzata nei laboratori finali:
- il programma da eseguire può essere letto da un file di testo `<filename>` con l’opzione `-i <filename>`, altrimenti viene letto dallo standard
input
- l'output del programma in esecuzione può essere salvato su un file di testo `<filename>` con l’opzione `-o <filename>`, altrimenti viene usato lo standard output
- l’opzione `-ntc` (abbreviazione di no-type-checking) permette di eseguire il programma senza effettuare prima il controllo di semantica statica del
typechecker 

## Definizione del linguaggio

### Sintassi
Il linguaggio contiene le nuove parole chiave `for` e `of` e i nuovi simboli `[`, `]` e `:`.

La sintassi del linguaggio è definita da questa grammatica non ambigua e in forma EBNF:

```
Prog ::= StmtSeq EOF
StmtSeq ::= Stmt (';' StmtSeq)?
Stmt ::= 'var'? IDENT '=' Exp | 'print' Exp |  'if' '(' Exp ')' Block ('else' Block)? | 'for' '(' 'var' IDENT 'of Exp ')' Block 
Block ::= '{' StmtSeq '}'
Exp ::= And (',' And)* 
And ::= Eq ('&&' Eq)* 
Eq ::= Add ('==' Add)*
Add ::= Mul ('+' Mul)*
Mul::= Unary ('*' Unary)*
Unary ::= 'fst' Unary | 'snd' Unary | '-' Unary | '!' Unary | Dict 
Dict ::= Atom ('[' Exp (':' Exp?)? ']')* 
Atom :: = '[' Exp ':' Exp ']' | BOOL | NUM | IDENT | '(' Exp ')'
```
La grammatica **non** richiede trasformazioni e può essere utilizzata così com'è per sviluppare un parser con un solo token di lookahead.

Rispetto al linguaggio del laboratorio, sono stati aggiunti
- il literal di tipo `dict` (dizionario)  `'[' Exp ':' Exp ']'`
- due operatori binari sui dizionari
  - accesso (get) `Exp '[' Exp ']'`
  - cancellazione (delete) `Exp '[' Exp ':' ']'`
- l'operatore  ternario di aggiornamento (update) di un dizionario `Exp '[' Exp ':' Exp ']'` 
- lo statement `'for' '(' 'var' IDENT 'of' Exp ')' Block`

Direttamente dalla definizione della grammatica si deduce che tutti gli operatori sui dizionari (get, delete e update) hanno lo stesso livello di priorità, 
associano da sinistra e hanno la precedenza sugli operatori unari `fst`, `snd`, `-` e `!`.

Per esempio, l'espressione `[0:1][1:2][0:][1]` è sintatticamente corretta e corrisponde alla sequenza di operazioni di update, delete e get (nell'ordine da sinistra a destra) sul literal `[0:1]`. 

Per ulteriori chiarimenti potete fare riferimento ai programmi in `tests/success` e `tests/failure/syntax`.

### Semantica statica e dinamica 
La semantica statica e dinamica del linguaggio sono definite in F# nel file `semantics/Semantics.fs`.
Il file `semantics/Program.fs` contiene un semplice esempio di programma corrispondente a `tests/success/prog01.txt`.
Esso può essere eseguito con il comando `dotnet run`. 

#### Semantica statica

Il costruttore `DictType of staticType` corrisponde al nuovo tipo `dict` dei dizionari costruiti a partire dal literal `'[' Exp ':' Exp ']'`.

Tutti i dizionari devono avere chiavi di tipo `IntType`, ma i valori associati alle chiavi possono essere di qualsiasi tipo, purché omogeneo
all'interno di uno stesso dizionario.

Per esempio, `DictType BoolType` è il tipo dei dizionari che associano alle chiavi valori booleani;
`DictType(DictType(PairType(IntType,IntType)))` è il tipo dei dizionari che associano alle chiavi valori che, a loro volta,
sono dizionari e associano alle chiavi coppie di numeri interi.

##### Regole della semantica statica
- se `Exp1` ha tipo `IntType` e `Exp2` ha tipo `ty`, allora il literal `'[' Exp1 ':' Exp2 ']'` ha tipo `DictType ty`
- se `Exp1` ha tipo `DictType ty` e `Exp2` ha tipo `IntType`, allora l'espressione `Exp1 '[' Exp2 ':' ']'` ha tipo `DictType ty`
- se `Exp1` ha tipo `DictType ty` e `Exp2` ha tipo `IntType`, allora l'espressione `Exp1 '[' Exp2 ']'` ha tipo `ty`
- se `Exp1` ha tipo `DictType ty`, `Exp2` ha tipo `IntType` e `Exp3` ha tipo `ty` allora l'espressione `Exp1 '[' Exp2 ':' Exp3 ']'` ha tipo `DictType ty`
- se `Exp` ha tipo `DictType ty` rispetto all'ambiente statico corrente `env` e `Block` è corretto rispetto all'ambiente ottenuto aggiungendo a `env` un nuovo scope annidato dove l'unica variabile dichiarata è `IDENT` di tipo `PairType(IntType,ty)`, allora lo statement `'for' '(' 'var' IDENT 'of' Exp ')' Block` è corretto e l'ambiente corrente `env` non viene modificato 

Per ulteriori chiarimenti potete fare riferimento ai programmi in `tests/success`, `tests/failure/static-semantics` e `tests/failure/static-semantics-only`.

#### Semantica dinamica

Il costruttore `DictValue of Map<int, value>` rappresenta i valori di tipo dizionario attraverso il tipo predefinito in F# `Map<int, value>` delle mappe 
con chiavi di tipo `int` e valori di tipo `value`. 

*Note importanti sui valori di tipo dizionario*
- Le chiavi risultano ordinate secondo l'ordine naturale dei numeri interi.

  Nell'implementazione in Java si consiglia di usare la classe predefinita `TreeMap<K,V>` del package `java.util`.
- Diversamente dai requisiti della semantica statica, la semantica dinamica non impone che un dizionario debba contenere valori di tipo omogeneo.

  Per esempio, il programma `print [0:1][1:true][1]` stampa `true` se eseguito con l'opzione `-ntc` (no-type-checking). 

##### Regole della semantica dinamica

- se `Exp1` si valuta in un valore di tipo intero `key` e `Exp2` in un valore `val`, allora l'espressione `'[' Exp1 ':' Exp2 ']'` si valuta in un nuovo dizionario con l'unica chiave `key` e il valore `val` associato a essa. Viene sollevata un'eccezione se `key` non è un valore di tipo intero
- se `Exp1` si valuta in un dizionario `dict` e `Exp2` in un valore di tipo intero `key`, allora l'espressione `Exp1 '[' Exp2 ':' ']'` si valuta in un nuovo dizionario `dict'` che contiene le stesse chiavi e valori associati in `dict`, eccetto la chiave `key` che non è presente in `dict'`. Viene sollevata un'eccezione se `dict` non è un valore di tipo dizionario, oppure `key` non è un valore di tipo intero, oppure `key` non è una chiave presente nel dizionario `dict` 
- se `Exp1` si valuta in un dizionario `dict` e `Exp2` in un valore di tipo intero `key`, allora l'espressione `Exp1 '[' Exp2 ']'` si valuta nel valore associato alla chiave `key` nel dizionario `dict`. Viene sollevata un'eccezione se `dict` non è un valore di tipo dizionario, oppure `key` non è un valore di tipo intero, oppure `key` non è una chiave presente nel dizionario `dict`
- se `Exp1` si valuta in un dizionario `dict`, `Exp2` in un valore di tipo intero `key` e `Exp3` in un valore `val`, allora l'espressione `Exp1 '[' Exp2 ':' Exp3 ']'` si valuta in un nuovo dizionario `dict'` che contiene le stesse chiavi e valori associati in `dict`, eccetto la chiave `key` che è associata a `val` in `dict'`. Viene sollevata un'eccezione se `dict` non è un valore di tipo dizionario oppure `key` non è un valore di tipo intero
- se `Exp` si valuta in un dizionario `dict`, allora l'esecuzione dello statement `'print' Exp` non modifica l'ambiente dinamico e stampa tra parantesi quadre tutte le associazioni `key:value` in `dict` nell'ordine crescente delle chiavi e separate da una virgola senza alcun spazio. Per esempio `print [3:5,0][2:4,1][1:3,2]` stampa la stringa `[1:(3,2),2:(4,1),3:(5,0)]`
- se `Exp` si valuta in un dizionario `dict`, allora lo statement `'for' '(' 'var' IDENT 'of' Exp ')' Block` esegue iterativamente per ogni coppia `(key,value)` in `dict` il blocco `Block` assegnando prima tale coppia alla variabile `IDENT`. Quindi il numero totale di cicli eseguiti coincide con il numero di chiavi contenute in `dict`.

  L'ambiente dinamico rispetto al quale viene eseguito `block` per la prima volta (assumendo che `dict` non sia vuoto) è ottenuto aggiungendo all'ambiente corrente un nuovo scope annidato dove l'unica variabile dichiarata è `IDENT`, inizializzata con un qualsiasi valore (per esempio 0).
  
  Per le iterazioni successive alla prima (se `dict` ha più di una chiave), l'ambiente dinamico rispetto al quale viene eseguito `block` è ottenuto aggiornando nell'ambiente risultante dopo l'esecuzione di `block` al ciclo precedente il valore della variabile `IDENT` con la coppia `(key,value)` di `dict` considerata nel ciclo corrente.

  L'ambiente dopo l'esecuzione del `'for'` corrisponde a quello ottenuto dall'esecuzione di `block` nell'ultima iterazione dove lo scope più annidato che contiene la variabile `IDENT` del `'for'` è stato eliminato.

  Se `dict` è vuoto, allora l'esecuzione del `'for'` non ha alcun effetto sull'ambiente.
 
  *Note importanti sull'esecuzione dello statement `'for'`*
  - l'espressione `exp` viene valutata una volta sola, all'inizio dell'esecuzione del `'for'`
  - l'esecuzione del `'for'` considera le coppie `(key,value)` del dizionario rispetto all'ordine crescente delle chiavi

    Esempio: l'esecuzione del programma
    ```
    for(var p of [3:5][2:4][1:3]){print p}
    ```
    stampa
    ```
    (1,3)
    (2,4)
    (3,5)
    ```
    Il file `tests/success/prog08.txt` contiene un esempio simile.

  *Nota importante sulla semantica dinamica degli operatori su dizionari*

  Gli operatori su dizionari sono *funzionali*, quindi la loro valutazione non può modificare valori di tipo dizionario già presenti nell'ambiente.

  Per esempio il programma nel file `tests/success/prog05.txt` stampa `true`:
  ```
  var d1=[1:3];
  var d2=d1[1:4];
  print d1[1]==3&&d2[1]==4 // prints true
  ```

### Contenuto del repository

* `semantics/Semantica.fs` : semantica statica e dinamica del linguaggio definita in F#
* `semantics/Program.fs` : contiene un semplice esempio di programma tradotto in F#, corrispondente a `tests/success/prog01.txt`, eseguibile rispetto alla semantica definita in `semantics/Semantics.fs`
* `tests/success`: test corretti anche **senza** l'opzione `-ntc`
* `tests/failure/syntax`: test con errori di sintassi 
* `tests/failure/static-semantics`: test con errori statici **senza** l'opzione `-ntc` ed errori dinamici **con** l'opzione `-ntc`
* `tests/failure/static-semantics-only`: test con errori statici **senza** l'opzione `-ntc` e corretti con l'opzione `-ntc`
* `tests/failure/dynamic-semantics`: test che generano errori dinamici **con** o **senza** l'opzione `-ntc`

## Modalità di consegna

- La consegna è valida solo se il **progetto passa tutti i test** contenuti nel folder `tests`; la valutazione del progetto tiene conto dell'esecuzione di test aggiuntivi e della qualità del codice
- È possibile consegnare il progetto alcuni giorni prima delle date delle prove scritte.
  Il calendario delle scadenze per le consegne è: **17 giugno**, **12 luglio**, **6 settembre**, **13 gennaio** e **31 gennaio**.

  Dopo ogni scadenza, vengono corretti tutti i progetti consegnati e pubblicati i relativi risultati prima che le consegne siano riaperte.

  **Dopo l'ultima scadenza del 31 gennaio non sarà più possibile consegnare progetti validi per l'anno accademico in corso**
- Il progetto può essere consegnato anche se l'esame scritto non è stato ancora superato
- Dopo il commit (e push) finale del progetto su GitHub, la consegna va segnalata da **un singolo componente del gruppo** utilizzando [AulaWeb](https://2023.aulaweb.unige.it/course/view.php?id=6694) e indicando **il numero del gruppo** definito nell'[elenco su AulaWeb](https://2023.aulaweb.unige.it/mod/wiki/view.php?id=68156)
- Per ricevere supporto durante lo sviluppo del progetto è consigliabile tenere sempre aggiornato il codice del progetto sul repository GitHub  
- Dopo che il progetto è stato valutato positivamente, il relativo colloquio **individuale** può essere sostenuto  anche se l'esame scritto non è stato ancora superato; esso ha lo scopo di verificare che ogni componente del gruppo abbia compreso il funzionamento del codice e abbia contribuito attivamente al suo sviluppo
- L'**OpenBadge Soft skills - Sociale base 1 - A** verrà assegnato ai componenti del gruppo solo se **tutti** avranno superato positivamente (ossia senza decremento del punteggio) il colloquio individuale
- Per ulteriori informazioni consultare la [pagina AulaWeb sulle modalità di esame](https://2023.aulaweb.unige.it/mod/page/view.php?id=68149)

javac progetto2024/parser/ast/*.java progetto2024/environments/*.java progetto2024/parser/*.java progetto2024/visitors/execution/*.java progetto2024/visitors/typechecking/*.java progetto2024/visitors/*.java progetto2024/Main.java .\progetto2024\Mainparser.java