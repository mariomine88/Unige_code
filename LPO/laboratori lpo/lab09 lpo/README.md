# Laboratorio di LPO, 16 maggio 2024: implementazione di un interprete con visitor pattern

### Scopo del laboratorio
Questa attività di laboratorio è dedicata al completamento dell'implementazione del linguaggio di programmazione di cui è stato sviluppato il parser nel laboratorio precedente. Per sviluppare correttamente il codice mancante è necessario comprendere la specifica della semantica statica e dinamica del linguaggio e il codice già presente; i package `lab09.parser` e `lab09.parser.ast` che implementano il parser e
`lab09.environments` per  l'ambiente statico e dinamico delle variabili sono completi.

La semantica statica e dinamica vengono implementate con visite dell'albero della sintassi astratta (AST) generato dal parser, utilizzando il
*visitor pattern* (vedere [la lezione](https://2023.aulaweb.unige.it/mod/resource/view.php?id=141696) e il [codice di esempio](https://2023.aulaweb.unige.it/mod/folder/view.php?id=142941)).

### Definizione della semantica in F#
Come spiegato a [lezione](https://2023.aulaweb.unige.it/mod/resource/view.php?id=140421), la semantica statica e dinamica del linguaggio sono
definite ed eseguibili tramite un programma F# contenuto nel file `semantics/Semantics.fs`, con alcuni esempi di test eseguibili in `semantics/Program.fs`. 
In esso sono definiti i nodi dell'albero della sintassi astratta, i tipi della semantica statica (i tipi atomici `IntType` e `BoolType` e il tipo composto `PairType`), i valori della semantica dinamica (interi, booleani e coppie), scope e ambiente (environment) per la gestione delle variabili, le eccezioni che corrispondono ai vari errori della semantica statica e dinamica, le funzioni semantiche principali  (`typecheckProg`, `typecheckStmt`, `typecheckBlock`, `typecheckStmtSeq`, `typecheckExp` per la semantica statica e `executeProg`, `executeStmt`, `executeBlock`, `executeStmtSeq`, `evalExp` per quella dinamica), più altre definizioni ausiliarie.

### Implementazione in Java dell'ambiente delle variabili 
Il programma `semantics/Semantics.fs` fornisce una semantica precisa	e concisa del linguaggio, ma non efficiente, in quanto basata sul
paradigma funzionale. L'implementazione in Java è più efficiente grazie all'uso di oggetti mutabili; per esempio, quelli che modellano gli ambienti.

Prima di iniziare lo sviluppo del codice  è necessario comprendere bene il package `lab09.environments` e la sua relazione con la specifica `semantics/Semantics.fs`. 
Uno scope generico è un oggetto di tipo `java.util.HashMap<lab09.parser.ast.NamedEntity,T>` che implementa un dizionario con chiavi di tipo `lab09.parser.ast.NamedEntity` e valori di tipo generico `T`; il parametro di tipo `T` permette di usare lo stesso codice per la semantica statica e dinamica. Nel primo caso il parametro `T` corrisponde a `lab09.visitors.typechecking.Type` (`lab09.visitors.typechecking.StaticEnv` è sotto-tipo di `lab09.environmentsGenEnvironment<lab09.visitors.typechecking.Type>`), nel secondo a `lab09.visitors.execution.Value` (`lab09.visitors.execution.DynamicEnv` è sotto-tipo di `lab09.environmentsGenEnvironment<lab09.visitors.execution.Value>`). 

**Importante**: l'implementazione delle variabili tramite il record `lab09.parser.ast.Variable` assicura il corretto funzionamento dei metodi della classe `java.util.HashMap` che utilizzano il codice hash delle variabili per le varie operazioni sugli scope.
Infatti, nei record Java i metodi `equals` e `hashCode` di `Object ` sono automaticamente ridefiniti in modo che gli oggetti risultino uguali e abbiano lo stesso codice hash se hanno i valori dei campi uguali (nel caso di `lab09.parser.ast.Variable`
l'unico campo è `name` di tipo `String`). L'uso di una classe per definire le variabili avrebbe richiesto una ridefinizione esplicita
di `equals` e `hashCode`.

Un ambiente è una lista di tipo `java.util.LinkedList` che contiene scope ordinati per annidamento: il primo elemento della lista è lo scope più annidato, l'ultimo è quello più esterno. Tutti i metodi dell'interfaccia `lab09.environments.Environment` sono utilizzati nell'implementazione della semantica statica e dinamica, eccetto il metodo `update()` che è richiesto solamente dall'implementazione della semantica dinamica dello statement di assegnazione.

### Implementazione dei tipi in Java
I tipi atomici (ossia che non sono costruiti a partire da altri tipi più semplici) `IntType` e `BoolType` sono rappresentati dalle costanti `enum`  `BOOL` e `INT`   di tipo `lab09.visitors.typechecking.AtomicType`, mentre il tipo composto `PairType` è implementato dalla classe `lab09.visitors.typechecking.PairType`.

L'interfaccia `lab09.visitors.typechecking.Type` rappresenta l'insieme di tutti i possibili tipi e contiene metodi di default ausiliari che facilitano le operazioni di controllo dei tipi implementati nel typechecker.

### Implementazione dei valori in Java
I valori atomici (ossia che non sono costruiti a partire da altri valori più semplici) degli interi e dei booleani sono implementati dalle classi `lab09.visitors.execution.IntValue` e `lab09.visitors.execution.BoolValue`, che estendono la classe `lab09.visitors.execution.AtomicValue<T>`. Il tipo generico `T` corrisponde a classi Java predefinite 
come `Integer` e `Boolean`. Le coppie di valori sono implementate dalla classe `lab09.visitors.execution.PairValue`.

**Importante**: i metodi `equals()` e `hashCode()` sono stati ridefiniti per gestire correttamente l'operatore di uguaglianza tra valori, così come il metodo `toString()`, necessario per l'esecuzione dello statement `print`. 

L'interfaccia `lab09.visitors.execution.Value` rappresenta l'insieme di tutti i possibili valori e contiene metodi di default di conversione
che sono necessari per due motivi strettamente correlati:
- per assicurare che il codice dell'interprete sia corretto dal punto di vista dei tipi. Per esempio, il metodo `getFstVal()` utilizzato per l'operazione del linguaggio `fst` è definito solo nella classe `PairValue` e non nell'interfaccia `Value`;
- per controllare dinamicamente che i tipi dei valori siano corretti quando l'interprete viene eseguito con l'opzione `-ntc` (no typechecking).
I metodi `visitAdd()` e `visitNot()` nella classe `lab09.visitors.execution.Execute` sono due esempi d'uso dei metodi di conversione.

Il comportamento di default dei metodi di conversione è sollevare un'eccezione di tipo `lab09.visitors.execution.InterpreterException`; i metodi sono ridefiniti nelle classi che implementano `lab09.visitors.execution.Value`, quando la conversione è corretta; per esempio, il metodo `int toInt()` è ridefinito nella classe `lab09.visitors.execution.IntValue` in modo che restituisca il numero contenuto nell'oggetto su cui viene chiamato.

### Metodi da completare
Sono da completare i metodi che implementano la semantica statica e dinamica mediante il visitor pattern nelle classi
`lab09.visitors.typechecking.TypeCheck`e `lab09.visitors.execution.Execute`, fatta eccezione per `visitMyLangProg`,
`visitPrintStmt`, `visitAdd` e `visitNot`.


È importante notare le differenze tra le definizioni delle funzioni semantiche in F# che visitano l'AST e i metodi di visita delle
classi `lab09.visitors.typechecking.Typecheck` e `lab09.visitors.execution.Execute`; tali diversità sono dovute all'uso di due paradigmi di programmazione diversi, quello funzionale senza nozione di stato modificabile (F#) e quello object-oriented con oggetti modificabili (Java).

* In Java gli ambienti sono modificabili e gli oggetti visitor contengono il campo `env` (l'ambiente statico o dinamico) che fa riferimento a un oggetto che viene via via modificato durante la visita dell'AST mediante i metodi dell'interfaccia `lab09.environments.Environment`.
* I metodi di visita non hanno parametri di tipo `lab09.environments.Environment` né restituiscono risultati di tipo `lab09.environments.Environment`; invece, vengono restituiti risultati di tipo `lab09.visitors.typechecking.Type`o `lab09.visitors.execution.Value`  che sono diversi da `null` solo per i nodi di tipo `lab09.parser.ast.Exp`; infatti, la visita dei nodi di tipo `lab09.parser.ast.Prog`, `lab09.parser.ast.Stmt` e `lab09.parser.ast.StmtSeq` non restituisce alcun tipo o valore.


### Tests
Sono disponibili alcuni test:
- `tests/success`: programmi corretti rispetto alla sintassi e ai tipi
- `tests/failure/syntax`: programmi con errori di sintassi (come nel laboratorio precedente)
- `tests/failure/static-semantics/`: programmi corretti sintatticamente, ma con errori di tipo
- `tests/failure/static-semantics-only/`: programmi corretti sintatticamente che sono eseguiti senza errori con l'opzione `-ntc` (no typechecking) nonostante contengano degli errori di tipo
