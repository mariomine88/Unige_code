package lab09.parser;

import lab09.parser.ast.Prog;

public interface Parser extends AutoCloseable {

	Prog parseProg() throws ParserException;

}