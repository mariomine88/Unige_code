package lab08.parser;

import static lab08.parser.TokenType.*;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.LineNumberReader;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.MatchResult;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


public class MyLangTokenizer implements Tokenizer {

	private static final String regEx; // the regular expression including all valid lexems

	/* symbol and keyword tables */
	private static final Map<String, TokenType> symbols = new TreeMap<>(); 
	private static final Map<String, TokenType> keywords = new HashMap<>(); 
	
	private final LineNumberReader bufReader; // the numbered buffered reader used by the buffered tokenizer
	private String line; // currently processed line
	private final Matcher matcher = Pattern.compile(regEx).matcher(""); // the matcher used by the tokenizer
	private MatchResult result; // the current result of the match
	
	static { // initialization of the symbol and keyword tables: symbols and keywords are singleton lexical categories 
		
		symbols.put("=", ASSIGN);
		symbols.put("-", MINUS);
		symbols.put("+", PLUS);
		symbols.put("*", TIMES);
		symbols.put("!", NOT);
		symbols.put("&&", AND);
		symbols.put("==", EQ);
		symbols.put(";", STMT_SEP);
		symbols.put(",", PAIR_OP);
		symbols.put("(", OPEN_PAR);
		symbols.put(")", CLOSE_PAR);
		symbols.put("{", OPEN_BLOCK);
		symbols.put("}", CLOSE_BLOCK);
		
		keywords.put("print", PRINT);
		keywords.put("var", VAR);
		keywords.put("false", BOOL);
		keywords.put("true", BOOL);
		keywords.put("if", IF);
		keywords.put("else", ELSE);
		keywords.put("fst", FST);
		keywords.put("snd", SND);
	}

	static { 
		/* definition of the regular expressions of all valid lexemes */

		/* builds the regular expression for symbols 
		 * symbols must be in reversed String order because the regular expression operator '|' is left-preferential! 
		 * for instance '==' must come before '='
		 * 
		 * this is not needed for keywords, with the reasonable assumption that keywords' proper substrings cannot be keywords
		 */
		
		final var symbolList = new LinkedList<String>(); // symbols used in the regular expression																				
		for (var s : symbols.keySet())
			symbolList.addFirst(String.format("\\%s", String.join("\\", s.split("")))); // every char is pre-pended with "\\" to avoid regular expression syntax problems
		final var symbolRegEx = String.format("(?<%s>%s)", SYMBOL.name(), String.join("|", symbolList)); // symbols
		/* builds the regular expressions for the other groups
		 * remark: keywordRegEx uses word boundary '\b' since keywords match only if the next symbol is not a letter */
		final var keywordRegEx = String.format("(?<%s>%s\\b)", KEYWORD.name(),
				String.join("|", keywords.keySet())); // keywords
		final var skipRegEx = String.format("(?<%s>\\s+|//.*)", SKIP.name()); // white spaces or single line comments to be skipped
		final var identRegEx = String.format("(?<%s>[a-zA-Z]\\w*)", IDENT.name()); // identifiers
		final var numRegEx = String.format("(?<%s>0|[1-9][0-9]*)", NUM.name()); // radix 10 natural numbers
		/* builds the complete regular expression as union of the different  groups
		 * remark: keywordRegEx must come before identRegEx because the '|' operator is left-preferential
		 * example: 'if' is a keyword but not an identifier */
		regEx = String.join("|", symbolRegEx, keywordRegEx, skipRegEx, identRegEx,
				numRegEx); 
	}

	public MyLangTokenizer(BufferedReader br) {
		this.bufReader = new LineNumberReader(br);
	}

	private boolean hasNext() throws TokenizerException { // checks whether there are still lexemes
		if (matcher.regionEnd() > matcher.regionStart()) // the matcher has still to complete the current line
			return true;
		while (true) { // reads the next non empty line, if any
			try {
				line = bufReader.readLine();
			} catch (IOException e) {
				throw new TokenizerException(e);
			}
			if (line == null)
				return false; // EOF reached
			if (line.isEmpty()) // yep, lines can be empty!
				continue;
			matcher.reset(line); // reset the matcher with the new non empty line
			return true;
		}
	}

	// returns the token type corresponding to the group name that matched
	// pre-condition: matcher.lookingAt() returned true
	private TokenType groupName() { 
		for (var groupName : result.namedGroups().keySet())
			if (result.group(groupName) != null)
				return TokenType.valueOf(groupName);
		throw new AssertionError("Fatal error: could not determine the token type!");
	}

	// returns the token type corresponding to the recognized lexeme 
	// pre-condition: matcher.lookingAt() returned true
	public TokenType tokenType() { // pre-condition: matcher.lookingAt() returned true
		var type = groupName();
		return switch (type) {
		case SYMBOL -> symbols.get(result.group());
		case KEYWORD -> keywords.get(result.group());
		default -> type;
		};
	}
	
	private void resetState() {
		result = null;
	}

	private void unrecognizedToken() throws TokenizerException {
		throw new TokenizerException(String.format("on line %s unrecognized token starting at '%s'",
				bufReader.getLineNumber(), line.substring(matcher.regionStart())));
	}

	public TokenType next() throws TokenizerException {
		resetState();
		TokenType tokenType = null;
		do {
			if (!hasNext()) { // builds a matcher and a result matching group name 'EOF.name()' with the empty lexeme 
				var m = Pattern.compile(String.format("(?<%s>)",EOF.name())).matcher("");
				m.matches();
				result = m.toMatchResult();
				return EOF;
			}
			if (!matcher.lookingAt())
				unrecognizedToken();
			result = matcher.toMatchResult();
			tokenType = tokenType();
			matcher.region(matcher.end(), matcher.regionEnd()); // advances in the matcher
		} while (tokenType == SKIP); // keeps advancing when skippable tokens are recognized
		return tokenType;
	}

	private void checkLegalState() {
		if (result == null)
			throw new IllegalStateException("No token was recognized");
	}

	private void checkLegalState(TokenType tokenType) {
		checkLegalState();
		if (this.tokenType() != tokenType)
			throw new IllegalStateException(String.format("No token of type %s was recognized", tokenType));
	}

	@Override
	public String tokenString() { // lexeme of the most recently recognized token, if any
		checkLegalState();
		return result.group();
	}

	@Override
	public boolean boolValue() { // boolean value of the most recently recognized token, if of type BOOL
		checkLegalState(BOOL);
		return Boolean.parseBoolean(result.group());
	}

	@Override
	public int intValue() { // integer value of the most recently recognized token, if of type NUM
		checkLegalState(NUM);
		return Integer.decode(result.group());
	}

	@Override
	public int getLineNumber() {
		return bufReader.getLineNumber();
	}

	@Override
	public void close() throws IOException { // tokenizers are auto-closeable
		if (bufReader != null)
			bufReader.close();
	}

}
