package lab07;

import java.util.Comparator;

public class ComparePersonBySurname implements Comparator<Person> {

	// compares 'Person' objects by 'surname' with the natural order of 'String'  
	// if the 'surname' fields are equal, then the natural order on 'id' is considered
	@Override
	public int compare(Person p1, Person p2) {
        return Comparator.comparing(Person::surname).thenComparingLong(Person::id).compare(p1, p2);
	}

}
