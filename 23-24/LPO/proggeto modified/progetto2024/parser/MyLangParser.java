package progetto2024.parser;

import java.io.IOException;
import static java.util.Objects.requireNonNull;
import static progetto2024.parser.TokenType.*;
import progetto2024.parser.ast.*;


/*
Prog ::= StmtSeq EOF
StmtSeq ::= Stmt (';' StmtSeq)?
Stmt ::= 'var'? IDENT '=' Exp | 'print' Exp |  'if' '(' Exp ')' Block ('else' Block)? | 'for' '(' 'var' IDENT 'of Exp ')' Block 
Block ::= '{' StmtSeq '}'
Exp ::= And (',' And)* 
And ::= Eq ('&&' Eq)* 
Eq ::= Add ('==' Add)*
Add ::= Mul ('+' Mul)*
Mul::= Div ('*' Div)*
Div::= Unary ('\' Unary)*
Unary ::= 'fst' Unary | 'snd' Unary | '-' Unary | '!' Unary | Dict 
Dict ::= Atom ('[' Exp (':' Exp?)? ']')* 
Atom :: = '[' Exp ':' Exp ']' | BOOL | NUM | IDENT | '(' Exp ')'
*/

public class MyLangParser implements Parser {

	private final MyLangTokenizer tokenizer; // the tokenizer used by the parser

	/*
	 * reads the next token through the  tokenizer associated with the
	 * parser; TokenizerExceptions are chained into corresponding ParserExceptions
	 */
	private void nextToken() throws ParserException {
		try {
			tokenizer.next();
		} catch (TokenizerException e) {
			throw new ParserException(e);
		}
	}

	// decorates error message with the corresponding line number
	private String lineErrMsg(String msg) {
		return String.format("on line %s: %s", tokenizer.getLineNumber(), msg);
	}

	/*
	 * checks whether the token type of the currently recognized token matches
	 * 'expected'; if not, it throws a corresponding ParserException
	 */
	private void match(TokenType expected) throws ParserException {
		final var found = tokenizer.tokenType();
		if (found != expected)
			throw new ParserException(
					lineErrMsg(String.format("Expecting %s, found %s('%s')", expected, found, tokenizer.tokenString())));
	}

	/*
	 * checks whether the token type of the currently recognized token matches
	 * 'expected'; if so, it reads the next token, otherwise it throws a
	 * corresponding ParserException
	 */
	private void consume(TokenType expected) throws ParserException {
		match(expected);
		nextToken();
	}

	// throws a ParserException because the current token was not expected
	private <T> T unexpectedTokenError() throws ParserException {
		throw new ParserException(lineErrMsg(
				String.format("Unexpected token %s ('%s')", tokenizer.tokenType(), tokenizer.tokenString())));
	}

	// associates the parser with a corresponding non-null  tokenizer
	public MyLangParser(MyLangTokenizer tokenizer) {
		this.tokenizer = requireNonNull(tokenizer);
	}

	/*
	 * parses a program Prog ::= StmtSeq EOF
	 */
	@Override
	public Prog parseProg() throws ParserException {
		nextToken(); // one look-ahead symbol
		final var prog = new MyLangProg(parseStmtSeq());
		match(EOF); // last token must have type EOF
		return prog;
	}

	@Override
	public void close() throws IOException {
		if (tokenizer != null)
			tokenizer.close();
	}

	/*
	 * parses a non empty sequence of statements, binary operator STMT_SEP is right
	 * associative StmtSeq ::= Stmt (';' StmtSeq)?
	 */
	private StmtSeq parseStmtSeq() throws ParserException {
		final var stmt = parseStmt();
		StmtSeq stmtSeq;
		if (tokenizer.tokenType() == STMT_SEP) {
			nextToken();
			stmtSeq = parseStmtSeq();
		} else
			stmtSeq = new EmptyStmtSeq();
		return new NonEmptyStmtSeq(stmt, stmtSeq);
	}

	/*
	 * parses a statement Stmt ::= 'var'? IDENT '=' Exp | 'print' Exp | 'if' '(' Exp
	 * ')' Block ('else' Block)?
	 */
	private Stmt parseStmt() throws ParserException {
		return switch (tokenizer.tokenType()) {
		case PRINT -> parsePrintStmt();
		case VAR -> parseVarStmt();
		case IDENT -> parseAssignStmt();
		case IF -> parseIfStmt();
		case FOR -> parseForStmt();
		default -> unexpectedTokenError();
		};
	}

	/*
	 * parses the 'print' statement Stmt ::= 'print' Exp
	 */
	private PrintStmt parsePrintStmt() throws ParserException {
		consume(PRINT); 
		return new PrintStmt(parseExp());
	}

	/*
	 * parses the 'var' statement Stmt ::= 'var' IDENT '=' Exp
	 */
	private VarStmt parseVarStmt() throws ParserException {
		consume(VAR); 
		final var var = parseVariable();
		consume(ASSIGN);
		return new VarStmt(var, parseExp());
	}

	/*
	 * parses the assignment statement Stmt ::= IDENT '=' Exp
	 */
	private AssignStmt parseAssignStmt() throws ParserException {
		final var var = parseVariable();
		consume(ASSIGN);
		return new AssignStmt(var, parseExp());
	}

	/*
	 * parses the 'if' statement Stmt ::= 'if' '(' Exp ')' Block ('else' Block)?
	 */
	private IfStmt parseIfStmt() throws ParserException {
		consume(IF);
		final var exp = parseRoundPar();
		final var thenBlock = parseBlock();
		if (tokenizer.tokenType() != ELSE)
			return new IfStmt(exp, thenBlock);
		nextToken();
		return new IfStmt(exp, thenBlock, parseBlock());
	}

	/*
	 * parses the 'for' statement Stmt ::= 'for' '(' 'var' IDENT 'of' Exp ')' Block
	 */
	private ForStmt parseForStmt() throws ParserException{
		consume(FOR);
		consume(OPEN_PAR);
		consume(VAR); 
		final var var = parseVariable();
		consume(OF);
		final var exp = parseExp();
		consume(CLOSE_PAR);
		final var block = parseBlock();
		return new ForStmt(var, exp, block);
	}

	/*
	 * parses a block of statements Block ::= '{' StmtSeq '}'
	 */
	private Block parseBlock() throws ParserException {
		consume(OPEN_BLOCK);
		final var stmts = parseStmtSeq();
		consume(CLOSE_BLOCK);
		return new Block(stmts);
	}

	/*
	 * parses expressions, starting from the lowest precedence operator PAIR_OP
	 * which is left-associative Exp ::= And (',' And)*
	 */

	private Exp parseExp() throws ParserException {
		var exp = parseAnd();
		while (tokenizer.tokenType() == PAIR_OP) {
			nextToken();
			exp = new PairLit(exp, parseAnd());
		}
		return exp;
	}

	/*
	 * parses expressions, starting from the lowest precedence operator AND which is
	 * left-associative And ::= Eq ('&&' Eq)*
	 */
	private Exp parseAnd() throws ParserException {
		var exp = parseEq();
		while (tokenizer.tokenType() == AND) {
			nextToken();
			exp = new And(exp, parseEq());
		}
		return exp;
	}

	/*
	 * parses expressions, starting from the lowest precedence operator EQ which is
	 * left-associative Eq ::= Add ('==' Add)*
	 */
	private Exp parseEq() throws ParserException {
		var exp = parseAdd();
		while (tokenizer.tokenType() == EQ) {
			nextToken();
			exp = new Eq(exp, parseAdd());
		}
		return exp;
	}

	/*
	 * parses expressions, starting from the lowest precedence operator PLUS which
	 * is left-associative Add ::= Mul ('+' Mul)*
	 */
	private Exp parseAdd() throws ParserException {
		var exp = parseMul();
		while (tokenizer.tokenType() == PLUS) {
			nextToken();
			exp = new Add(exp, parseMul());
		}
		return exp;
	}

	/*
	 * parses expressions, starting from the lowest precedence operator TIMES which
	 * is left-associative Mul::= Unary ('*' Atom)*
	 */
	private Exp parseMul() throws ParserException {
		var exp = parseDiv();
		while (tokenizer.tokenType() == TIMES) {
			nextToken();
			exp = new Mul(exp, parseDiv());
		}
		return exp;
	}



	private Exp parseDiv() throws ParserException {
		var exp = parseUnary();
		while (tokenizer.tokenType() == DIV) {
			nextToken();
			exp = new Div(exp, parseUnary());
		}
		return exp;
	}

	/*
	 * parses expressions of type Atom Unary ::= 'fst' Unary | 'snd' Unary | '-' Unary | '!' Unary | Dict 
	 */

	 private Exp parseUnary() throws ParserException {
		return switch (tokenizer.tokenType()) {
		case MINUS -> parseMinus();
		case NOT -> parseNot();
		case FST -> parseFst();
		case SND -> parseSnd();
		default -> parseAtomOrparseDictAcc();
		};
	}

	/*
	 * parses expressions with unary operator MINUS Unary ::= '-' Unary
	 */
	private Sign parseMinus() throws ParserException {
		consume(MINUS); 
		return new Sign(parseUnary());
	}

	/*
	 * parses expressions with unary operator NOT Unary ::= '!' Unary
	 */
	private Not parseNot() throws ParserException {
		consume(NOT); 
		return new Not(parseUnary());
	}

	/*
	 * parses expressions with unary operator FST Unary ::= 'fst' Unary
	 */
	private Fst parseFst() throws ParserException {
		consume(FST);
		return new Fst(parseUnary());
	}

	/*
	 * parses expressions with unary operator SND Unary ::= 'snd' Unary
	 */
	private Snd parseSnd() throws ParserException {
		consume(SND); 
		return new Snd(parseUnary());
	}

	/*
	 * parses expressions of type Dict ::= Atom ('[' Exp (':' Exp?)? ']')* 

	* Parses dictionary access and modification expressions.
	* The grammar is defined as:
	*   DictAcc ::= Atom ('[' Exp (':' Exp?)? ']')*
	*
	* This parser handles three dictionary operations:
	*   1. Access (get): `Exp '[' Exp ']'`
	*   2. Deletion (delete): `Exp '[' Exp ':' ']'`
	*   3. Update (update): `Exp '[' Exp ':' Exp ']'`
	*/
	private Exp parseAtomOrparseDictAcc() throws ParserException {
		var exp = parseAtom();
		if (tokenizer.tokenType() == OPEN_DICT){
			while (tokenizer.tokenType() == OPEN_DICT) {
				nextToken();
				Exp key = parseExp();
				if (tokenizer.tokenType() == DICT_OP) {
					nextToken();
					if (tokenizer.tokenType() == CLOSE_DICT) {
						// Delete operation: Exp '[' Exp ':' ']'
						nextToken();
						exp = new DictDel(exp, key);
					} else {
						// Update operation: Exp '[' Exp ':' Exp ']'
						Exp value = parseExp();
						consume(CLOSE_DICT);
						exp = new DictUpdate(exp, key, value);
					}
				} else {
					// Access operation: Exp '[' Exp ']'
					consume(CLOSE_DICT);
					exp = new DictGet(exp, key);
				}
			}
		}
		return exp;
	 }


	/*
	 * parses expressions of type Atom Atom ::= '[' Exp ':' Exp ']' | BOOL | NUM | IDENT | '(' Exp ')'
	 */
	private Exp parseAtom() throws ParserException {
		return switch (tokenizer.tokenType()) {
		case NUM -> parseNum();
		case IDENT -> parseVariable();
		case OPEN_PAR -> parseRoundPar();
		case BOOL -> parseBoolean();
		case OPEN_DICT -> parseDictliteral();
		default -> unexpectedTokenError();
		};
	}

	// parses number literals
	private IntLiteral parseNum() throws ParserException {
		final var val = tokenizer.intValue();
		nextToken();
		return new IntLiteral(val);
	}

	// parses boolean literals
	private BoolLiteral parseBoolean() throws ParserException {
		final var val = tokenizer.boolValue();
		nextToken(); 
		return new BoolLiteral(val);
	}

	// parses variable identifiers
	private Variable parseVariable() throws ParserException {
		final var name = tokenizer.tokenString();
		consume(IDENT); 
		return new Variable(name);
	}


	/*
	 * parses expressions delimited by parentheses Atom ::= '(' Exp ')'
	 */

	private Exp parseRoundPar() throws ParserException {
		consume(OPEN_PAR); 
		final var exp = parseExp();
		consume(CLOSE_PAR);
		return exp;
	}

	/*
	 * parses expressions delimited by square brackets Atom ::= '[' Exp ':' Exp ']'
	 */	
	private DictLiteral parseDictliteral() throws ParserException {
		consume(OPEN_DICT);
		final var key = parseExp();
		consume(DICT_OP);
		final var value = parseExp();
		consume(CLOSE_DICT);
		return new DictLiteral(key, value);
	}

}
