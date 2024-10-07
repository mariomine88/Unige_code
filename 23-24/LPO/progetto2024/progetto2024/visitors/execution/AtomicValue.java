package progetto2024.visitors.execution;

import static java.util.Objects.requireNonNull;

public abstract class AtomicValue<T> implements Value {
	protected T value; // T expected to be a built-in Java class

	protected AtomicValue(T value) {
		this.value = requireNonNull(value);
	}

	@Override
	public final boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj instanceof AtomicValue<?> sv)
			return value.equals(sv.value);
		return false;
	}
	
	@Override
	public int hashCode() {
		return value.hashCode();
	}

	@Override
	public String toString() {
		return value.toString();
	}
}
