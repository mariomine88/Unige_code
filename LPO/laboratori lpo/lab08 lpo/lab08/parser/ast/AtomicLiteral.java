package lab08.parser.ast;

public abstract class AtomicLiteral<T> implements Exp {

	protected final T value;

	public AtomicLiteral(T n) {
		this.value = n;
	}

	@Override
	public String toString() {
		return String.format("%s(%s)", getClass().getSimpleName(), value);
	}
}
