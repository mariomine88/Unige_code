package lab09.visitors.typechecking;

import static java.util.Objects.requireNonNull;

public record PairType(Type fstType, Type sndType) implements Type {

	public static final String TYPE_NAME = "PAIR";

	public PairType {
		requireNonNull(fstType);
		requireNonNull(sndType);
	}

	@Override
	public String toString() {
		return String.format("(%s*%s)", fstType, sndType);
	}

}