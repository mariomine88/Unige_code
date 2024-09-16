package lab07;

import static java.util.Objects.hash;
import static java.util.Objects.requireNonNull;

public record Person(String name, String surname, long id) {

	private static void requireNonNeg(long id) {
		if (id < 0)
			throw new IllegalArgumentException("Person's id cannot be negative");
	}

	public Person {
		requireNonNull(name);
		requireNonNull(surname);
		requireNonNeg(id);
	}

	public static Person newOfNameSurnameId(String name, String surname, long id) {
		return new Person(name, surname, id);
	}

	// two 'Person' objects are equal iff they have the same 'id'
	@Override
	public final boolean equals(Object obj) {
	    return this.id == requireNonNull((Person) obj).id;
	}

	@Override
	public final int hashCode() {
	    return hash(id);
	}

	// converts into CSV format, keeps the order of fields declaration
	@Override
	public String toString() {
	    return name + "," + surname + "," + String.valueOf(id);
	}

}
