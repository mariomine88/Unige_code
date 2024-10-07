package progetto2024.visitors.typechecking;

public interface Type {
	default void checkEqual(Type found) throws TypecheckerException {
		if (!equals(found))
			throw new TypecheckerException(found.toString(), toString());
	}

	default PairType checkIsPairType() throws TypecheckerException {
		if (this instanceof PairType pt)
			return pt;
		throw new TypecheckerException(toString(), PairType.TYPE_NAME);
	}

	default Type getFstPairType() throws TypecheckerException {
		return checkIsPairType().fstType();
	}

	default Type getSndPairType() throws TypecheckerException {
		return checkIsPairType().sndType();
	}

	default DictType checkIsDictType() throws TypecheckerException {
		if (this instanceof DictType dt)
			return dt;
		throw new TypecheckerException(toString(), DictType.TYPE_NAME);
	}

	default Type getValueDictType() throws TypecheckerException {
		return checkIsDictType().valueType();
	}
}
