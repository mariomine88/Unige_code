package progetto2024.parser.ast;

import progetto2024.visitors.Visitor;

public interface AST {
	<T> T accept(Visitor<T> visitor);
}
