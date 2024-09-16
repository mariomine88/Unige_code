package lab08.parser;

import lab08.parser.ast.Prog;

public interface Parser extends AutoCloseable {

	Prog parseProg() throws ParserException;

}