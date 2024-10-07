package lab08.parser;

import java.io.IOException;

import lab08.parser.ast.*;

import static java.util.Objects.requireNonNull;
import static lab08.parser.TokenType.*;


/*
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
		default -> unexpectedTokenError();
		};
	}

	/*
	 * parses the 'print' statement Stmt ::= 'print' Exp
	 */
	private PrintStmt parsePrintStmt() throws ParserException {
		consume(PRINT); // or nextToken() since PRINT has already been recognized
		return new PrintStmt(parseExp());
	}

	/*
	 * parses the 'var' statement Stmt ::= 'var' IDENT '=' Exp
	 */
	private VarStmt parseVarStmt() throws ParserException {
		consume(VAR); // or nextToken() since VAR has already been recognized
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
		consume(IF); // or nextToken() since IF has already been recognized
		final var exp = parseRoundPar();
		final var thenBlock = parseBlock();
		if (tokenizer.tokenType() != ELSE)
			return new IfStmt(exp, thenBlock);
		nextToken();
		return new IfStmt(exp, thenBlock, parseBlock());
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
	 * is left-associative Mul::= Atom ('*' Atom)*
	 */
	private Exp parseMul() throws ParserException {
		var exp = parseAtom();
		while (tokenizer.tokenType() == TIMES) {
			nextToken();
			exp = new Mul(exp, parseAtom());
		}
		return exp;
	}

	/*
	 * parses expressions of type Atom Atom ::= 'fst' Atom | 'snd' Atom | '-' Atom |
	 * '!' Atom | BOOL | NUM | IDENT | '(' Exp ')'
	 */
	private Exp parseAtom() throws ParserException {
		return switch (tokenizer.tokenType()) {
		case NUM -> parseNum();
		case IDENT -> parseVariable();
		case MINUS -> parseMinus();
		case OPEN_PAR -> parseRoundPar();
		case BOOL -> parseBoolean();
		case NOT -> parseNot();
		case FST -> parseFst();
		case SND -> parseSnd();
		default -> unexpectedTokenError();
		};
	}

	// parses number literals
	private IntLiteral parseNum() throws ParserException {
		final var val = tokenizer.intValue();
		nextToken(); // if tokenizer.intValue() does not throw an exception, then NUM has been recognized
		return new IntLiteral(val);
	}

	// parses boolean literals
	private BoolLiteral parseBoolean() throws ParserException {
		final var val = tokenizer.boolValue();
		nextToken(); // if tokenizer.boolValue() does not throw an exception, then BOOL has been recognized
		return new BoolLiteral(val);
	}

	// parses variable identifiers
	private Variable parseVariable() throws ParserException {
		final var name = tokenizer.tokenString();
		consume(IDENT); // this check is necessary for parsing correctly the 'var' statement
		return new Variable(name);
	}

	/*
	 * parses expressions with unary operator MINUS Atom ::= '-' Atom
	 */
	private Sign parseMinus() throws ParserException {
		consume(MINUS); // or nextToken() since MINUS has already been recognized
		return new Sign(parseAtom());
	}

	/*
	 * parses expressions with unary operator FST Atom ::= 'fst' Atom
	 */
	private Fst parseFst() throws ParserException {
		consume(FST); // or nextToken() since FST has already been recognized
		return new Fst(parseAtom());
	}

	/*
	 * parses expressions with unary operator SND Atom ::= 'snd' Atom
	 */
	private Snd parseSnd() throws ParserException {
		consume(SND); // or nextToken() since SND has already been recognized
		return new Snd(parseAtom());
	}

	/*
	 * parses expressions with unary operator NOT Atom ::= '!' Atom
	 */
	private Not parseNot() throws ParserException {
		consume(NOT); // or nextToken() since NOT has already been recognized
		return new Not(parseAtom());
	}

	/*
	 * parses expressions delimited by parentheses Atom ::= '(' Exp ')'
	 */

	private Exp parseRoundPar() throws ParserException {
		consume(OPEN_PAR); // this check is necessary for parsing correctly the 'if' statement
		final var exp = parseExp();
		consume(CLOSE_PAR);
		return exp;
	}

}