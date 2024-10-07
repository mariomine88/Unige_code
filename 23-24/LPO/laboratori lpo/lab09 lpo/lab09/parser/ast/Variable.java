package lab09.parser.ast;

import static java.util.Objects.requireNonNull;

import lab09.visitors.Visitor;

public record Variable(String name) implements NamedEntity, Exp {

	public Variable {
		requireNonNull(name);
	}

	@Override
	public String toString() {
		return String.format("%s(%s)", getClass().getSimpleName(), name);
	}

	@Override
	public <T> T accept(Visitor<T> visitor) {
		return visitor.visitVariable(this);
	}
}
