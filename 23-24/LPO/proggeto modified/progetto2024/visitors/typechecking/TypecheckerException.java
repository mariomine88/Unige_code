package progetto2024.visitors.typechecking;

public class TypecheckerException extends RuntimeException {

	public TypecheckerException() {
	}

	public TypecheckerException(String found, String expected) {
		this(String.format("Found  %s, expected %s", found, expected));
	}

	public TypecheckerException(String message, Throwable cause, boolean enableSuppression,
			boolean writableStackTrace) {
		super(message, cause, enableSuppression, writableStackTrace);
	}

	public TypecheckerException(String message, Throwable cause) {
		super(message, cause);
	}

	public TypecheckerException(String message) {
		super(message);
	}

	public TypecheckerException(Throwable cause) {
		super(cause);
	}

}
