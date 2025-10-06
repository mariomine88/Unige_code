package lab09.parser.ast;

import lab09.visitors.Visitor;

public interface AST {
	<T> T accept(Visitor<T> visitor);
}
