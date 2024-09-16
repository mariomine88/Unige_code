# Laboratorio di LPO, 18 aprile 2024: parser top-down con un token di lookahead 

## Scopo del laboratorio

Questo laboratorio è dedicato allo sviluppo di un parser  top-down con un token di lookahead  per un semplice linguaggio di programmazione.
Per semplicità buona parte del codice è già presente nel repository, i principali obiettivi sono
- la comprensione del codice già presente;
- il completamento del codice di alcune classi (i dettagli si trovano in fondo a questo README).

Il materiale didattico di riferimento consiste nelle slide della [lezione sui parser top-down](https://2023.aulaweb.unige.it/mod/resource/view.php?id=136426) e nel  [relativo codice](https://2023.aulaweb.unige.it/mod/resource/view.php?id=136599).
### Specifica della sintassi del linguaggio
La grammatica EBNF del linguaggio si trova commentata all'inizio del file `lab08.parser.MyLangParser` già in forma adatta per sviluppare direttamenete il parser implementato nella classe `lab08.parser.MyLangParser`.
```txt
Prog ::= StmtSeq EOF
StmtSeq ::= Stmt (';' StmtSeq)?
Stmt ::= 'var'? IDENT '=' Exp | 'print' Exp |  'if' '(' Exp ')' Block ('else' Block)? 
Block ::= '{' StmtSeq '}'
Exp ::= And (',' And)* 
And ::= Eq ('&&' Eq)* 
Eq ::= Add ('==' Add)*
Add ::= Mul ('+' Mul)*
Mul::= Atom ('*' Atom)*
Atom ::= 'fst' Atom | 'snd' Atom | '-' Atom | '!' Atom | BOOL | NUM | IDENT | '(' Exp ')'
```
La grammatica si basa su alcune categorie lessicali definite in `lab08.parser.MyLangTokenizer` e associate a costanti di tipo 
`lab08.parser.TokenType`: la costante `IDENT` rappresenta gli identificatori di variabile, le costanti `BOOL` e `NUM` i literal di tipo booleano e naturale.
La costante `EOF` identifica il token end-of-file. I programmi corretti sintatticamente sono definiti dal non-terminale `Prog` e consistono di sequenze non vuote di istruzioni separate dal simbolo terminale `;`.

### Tokenizer
Il parser  `lab08.parser.MyLangParser` usa `lab08.parser.MyLangTokenizer` (il tokenizer che implementa l'interfaccia
`lab08.parser.Tokenizer`) e il tipo `lab08.parser.TokenType` di tutti i possibili token; entrambi i sorgenti nel repository sono completi e funzionanti. La nozione di token è un'astrazione della nozione di lessema
che permette di passare dalla sintassi concreta a quella astratta. Per esempio, il tipo  `STMT_SEP` corrisponde al token che separa due istruzioni;
il parser si riferisce a esso indipendentemente dalla sua sintassi concreta (il simbolo `;`). In questo modo il codice risulterà più leggibile e più facilmente modificabile: nel caso si volesse usare un simbolo diverso, basterà modificare `lab08.parser.MyLangTokenizer` lasciando invariato il codice del parser in `lab08.parser.MyLangParser`. In modo del tutto simile, vengono definiti i tipi di token per le
parole chiave (keyword), ossia quelle stringhe riservate che non possono essere usate come identificatori; per esempio, `PRINT` corrisponde alla parola chiave usata per l'istruzione di stampa; il parser si riferisce a questo tipo di token indipendentemente dalla sua rappresentazione concreta (la stringa `print`).

I tipi `SYMBOL`, `KEYWORD`, `SKIP` sono solo di utilità alla classe `lab08.parser.MyLangTokenizer` e non vengono utilizzati
all'interno di `lab08.parser.MyLangParser`.

I campi di classe `keywords` e `symbols` definiscono i dizionari che associano
alle parole chiavi e ai simboli di operazione il loro corrispondente tipo di token; i simboli sono stringhe di caratteri non alfanumerici, mentre le keyword sono stringhe di lettere che non possono essere usate come identificatori; vedere per esempio il programma `tests/failure/prog09.txt`.

È importante che le chiavi in `symbols` siano ordinate alfabeticamente per evitare problemi con simboli che sono la parte iniziale di altri,
come accade con `=` e `==`. Questo è dovuto al fatto che l'operatore `|` delle espressioni regolari dà la precedenza al primo operando;
quindi, l'espressione regolare `==|=` riconosce correttamente i due simboli, mentre `=|==` riconosce erroneamente due simboli
consecutivi `=` se l'input contiene la stringa "==".

I gruppi dell'espressione regolare contenuta nel campo `regEx` e usata dal `matcher` del tokenizer sono associati ai nomi dei tipi di token
`SYMBOL` (tutti i simboli di operazione), `KEYWORD` (tutte le parole chiave), `SKIP` (tutti gli spazi), `IDENT` e `NUM` correspondono
alle sotto-espressioni regolari che vengono composte assieme con l'operatore `|` per ottenere `regEx`:

```java
regEx = String.join("|", symbolRegEx, keywordRegEx, skipRegEx, identRegEx, numRegEx);
```
In questo modo il tokenizer riesce a individuare il tipo del token riconosciuto (metodo `tokenType()` definito a partire dal metodo `groupName()`)
mediante l'uso dei metodi di oggetto `namedGroups()`, `group(String)` e `group()` dell'interfaccia `java.util.regex.MatchResult` e il
metodo di classe `TokenType.valueOf(String)`.

L'uso di `import static lab08.parser.TokenType.*` permette di usare il nome semplice per riferirsi alle costanti di tipo `TokenType` all'interno di `lab08.parser.MyLangTokenizer`; per esempio,  `SKIP`, `IDENT` e `NUM` sono un'abbreviazione di `TokenType.SKIP`, `TokenType.IDENT` e `TokenType.NUM`.

Il tokenizer `lab08.parser.MyLangTokenizer` implementa l'interfaccia `lab08.parser.Tokenizer` con i seguenti metodi usati nella classe `lab08.parser.MyLangParser`:
```java
public interface Tokenizer extends AutoCloseable {

	TokenType next() throws TokenizerException;

	TokenType tokenType();

	String tokenString();

	int intValue();

	boolean boolValue();

	void close() throws IOException;

	int getLineNumber();
}
```
Il metodo  `next()` serve per avanzare nella lettura del buffered reader associato al tokenizer: il metodo
solleva l'eccezione controllata (checked) `TokenizerException` se non esiste un prossimo valido token, altrimenti restituisce
il tipo del token appena riconosciuto. Il tipo `SKIP` non viene mai restituito dal metodo `next()` ma è usato internamente al tokenizer
per gestire spazi bianchi e commenti, che vengono scartati.

Il metodo `tokenType()` restituisce il tipo del token appena riconosciuto (coincide con l'ultimo valore restituito da `next()`);
solleva l'eccezione `IllegalStateException` se nessun token è stato riconosciuto.

Il metodo `tokenString()` restituisce il lessema corrispondente al token appena riconosciuto; solleva l'eccezione
`IllegalStateException` se nessun token è stato riconosciuto.

Il metodo `intValue()` restituisce il valore del token di tipo `NUM` che è stato appena riconosciuto; 
 solleva l'eccezione `IllegalStateException` se nessun token di tipo `NUM` è stato riconosciuto.

Il metodo `boolValue()` restituisce il valore del token di tipo `BOOL` che è stato appena riconosciuto; 
 solleva l'eccezione `IllegalStateException` se nessun token di tipo `BOOL` è stato riconosciuto.

Il metodo `close()` è necessario perché la classe `MyLangTokenizer` implementa l'interfaccia `AutoCloseable`; ciò permette di usare il costrutto `try-with-resources` nel metodo `main` di `Main`, per gestire in modo automatico l'apertura e la chiusura dello stream di input; un commento analogo si applica alla classe `MyLangParser`.

Il metodo `getLineNumber()` restituisce la linea corrente analizzata dal tokenizer, grazie all'uso
di `java.io.LineNumberReader`; in questo modo i messaggi di errore di sintassi possono fare riferimento al corrispondente numero di linea per una maggiore chiarezza.

### Implementazione dell'albero della sintassi astratta (AST)
Il package `lab08.parser.ast` contiene tutte le definizioni per l'implementazione dell'albero della sintassi astratta (AST).
L'interfaccia `AST` introduce il tipo più generale che include qualsiasi tipo di nodo dell'AST; le sotto-interfacce `Prog`, `StmtSeq`, `Stmt`, `Exp` e `NamedEntity`
rappresentano sottotipi di nodi, corrispondenti alle categorie sintattiche
principali. In questo laboratorio le interfacce non contengono metodi, ma rappresentano solamente vari tipi di nodi
non compatibili tra di loro; per esempio, `Exp` non è sottotipo di `Stmt` e `Stmt` non è sottotipo di `Exp`, perché un'espressione non è uno statement e viceversa. Nei prossimi laboratori saranno presenti nelle interfacce anche dei metodi.

Alcune classi astratte permettono di fattorizzare codice riutilizzabile:
- `UnaryOp`: codice comune agli operatori unari;
- `BinaryOp`: codice comune agli operatori binari;
- `AtomicLiteral<T>`: codice comune alle foglie che corrispondono a literal di tipo atomico (come `int` e `boolean`);
- `AbstractAssignStmt`: codice comune agli statement di dichiarazione e assegnazione di una variabile.

Per le sequenze di elementi sintattici (per esempio `StmtSeq`), sarebbe possibile implementare
nodi con un numero variabile di figli, ma per semplicità vengono utilizzati nodi con numero costante di figli, nel seguente modo:

- un nodo di tipo `EmptyStmtSeq` corrisponde a una sequenza vuota di statement, ossia un nodo foglia senza figli.
- un nodo di tipo `NonEmptyStmtSeq` corrisponde a una sequenza non vuota di statement, ossia un nodo interno con due figli, uno di tipo `Stmt` e
l'altro di tipo `StmtSeq`.

Entrambe le classi riusano il codice delle classi generiche astratte `EmptySeq<T>` e `NonEmptySeq<FT,RT>`.

#### Importante
Per facilitare il testing, tutte le classi che implementano i nodi dell'AST ridefiniscono il metodo `String toString()` ereditato da `Object` per meglio visualizzare un AST. Vengono usati i metodi predefiniti `getClass()`
e `getSimpleName()` per accedere al nome della classe di un oggetto.
Per esempio, la stampa dell'AST generato dal parser a partire dal programma contenuto nel file ` tests/success/prog01.txt` produce il termine
```java
MyLangProg(NonEmptyStmtSeq(PrintStmt(Add(Sign(IntLiteral(40)),Mul(IntLiteral(5),IntLiteral(3)))),NonEmptyStmtSeq(PrintStmt(Sign(Mul(Add(IntLiteral(40),IntLiteral(5)),IntLiteral(3)))),EmptyStmtSeq)))
```

### Parser
Il codice del parser top-down può essere derivato direttamente dalla relativa grammatica che permette di usare un solo simbolo di lookahead.
La struttura della corrispondente classe `MyLangParser` è già totalmente definita, anche se alcuni metodi vanno completati. 

## Classi da completare

### Package `lab08.parser`
L'unica classe da completare è `MyLangParser`, in particolare i metodi

- `parseStmtSeq()`
- `parsePrintStmt()`
- `parseVarStmt()`
- `parseAssignStmt()`
- `parseIfStmt()`
- `parseBlock()`
- `parseAnd()`
- `parseEq()`
- `parseAdd()`
- `parseMul()`
- `parseNum()`
- `parseBoolean()`
- `parseVariable()`
- `parseMinus()`
- `parseFst()`
- `parseSnd()`
- `parseNot()`
- `parseRoundPar()`

### Package `lab08.parser.ast`
Completare le classi

- `AssignStmt`
- `VarStmt`
- `IfStmt`
- `Add`
- `Fst`


## Tests
Potete utilizzare i test nei seguenti folder
- `tests/success`: programmi corretti sintatticamente
- `tests/failure`: programmi con errori di sintassi

