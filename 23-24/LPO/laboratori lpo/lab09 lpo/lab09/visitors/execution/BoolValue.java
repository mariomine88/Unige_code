package lab09.visitors.execution;

public class BoolValue extends AtomicValue<Boolean> {

	public BoolValue(Boolean value) {
		super(value);
	}

	@Override
	public boolean toBool() {
		return value;
	}

}
