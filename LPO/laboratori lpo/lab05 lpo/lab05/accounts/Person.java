package lab05.accounts;

/*@ invariant:
 * name.matches(Person.validName) && surname.matches(Person.validName) && spouse!=this && 
 * \forall Person p1,p2; (p1.spouse==p2) == (p2.spouse==p1)
 */

public class Person implements Client {
	private final static String validName = "[A-Z][a-z]+( [A-Z][a-z]+)*";

	private final String name;
	private final String surname;
	private Person spouse; // optional :)

	// private auxiliary class methods for validation and security social number
	// generation

	private static String requireValidName(String name) {
		if (!name.matches(Person.validName)) // may throw NullPointerException
			throw new IllegalArgumentException("Illegal name: " + name);
		return name;
	}

	// public class methods to change the civil status of couples

	public static void join(Person p1, Person p2) {
		if (!p1.isSingle() || !p2.isSingle() || p1 == p2)
			throw new IllegalArgumentException();
		p1.spouse = p2;
		p2.spouse = p1;
	}

	public static void divorce(Person p1, Person p2) {
		if (p1 != p2.spouse)
			throw new IllegalArgumentException();
		p1.spouse = null; // throws NullPointerException if p1==null
		p2.spouse = null;
	}

	// constructor

	public Person(String name, String surname) {
		this.name = Person.requireValidName(name);
		this.surname = Person.requireValidName(surname);
	}

	// object methods

	public boolean isSingle() {
		return this.spouse == null;
	}

	// getters

	public String getName() {
		return this.name;
	}

	public String getSurname() {
		return this.surname;
	}

	public Person getSpouse() {
		return this.spouse;
	}

}