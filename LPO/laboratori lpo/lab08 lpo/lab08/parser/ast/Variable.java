package lab08.parser.ast;

import static java.util.Objects.requireNonNull;

public record Variable(String name) implements NamedEntity, Exp {

	public Variable {
		requireNonNull(name);
	}

	@Override
	public String toString() {
		return String.format("%s(%s)", getClass().getSimpleName(), name);
	}
}
