package lab07;

import java.io.PrintWriter;
import java.util.Map;
import java.util.Scanner;

public class CsvUtilitiesClass implements CsvUtilities {

	// reads from 'readable' a table in CSV format of 'Person' objects associated with 'score' 
	// groups by 'id', converts 'name' and 'surname' into upper case, and sums 'score' 
	// outputs the result in the dictionary 'output' where keys are 'Person' objects, and values their final 'Integer' 'score' 
	// may throw java.util.NoSuchElementException if some expected data are missing
	// or java.util.InputMismatchException or java.lang.IllegalArgumentException if some data does not match the expected type
	// additional columns are tacitly ignored
	@Override
	public void sumScoresGroupById(Readable readable, Map<Person, Integer> output) {
		try (var sc = new Scanner(readable)) {
			// (?m) means multi-line mode 
			// skips blanks at the beginning and end of each line
			// skips commas and blanks between them
			sc.useDelimiter("(?m)\\s*,\\s*|^\\s*|\\s*$"); 
			while (sc.hasNext()) {
				// reads the next three data: two strings ('name' and 'surname') and a long ('id')
				// creates a corresponding 'Person' object 'p' with the provided factory method
				// retrieves from 'output' the score associated with 'p', if any
				// reads the fourth element in the line: an int ('score')
				// updates in 'output' the score of 'p'
				// skips the remaining columns, if any
				var p = Person.newOfNameSurnameId(sc.next().toUpperCase(), sc.next().toUpperCase(), sc.nextLong());
				output.put(p, output.getOrDefault(p, 0) + sc.nextInt());
				if (sc.hasNextLine())
					sc.nextLine(); 
			}
		}
	}

	// writes a generic map into CSV format by using pw
	// if keys and values are structured, 
	// then columns are generated for all printable fields as defined by the corresponding 'toString()' method
	// key fields are printed prior to value fields
	public <K, V> void print(Map<K, V> map, PrintWriter pw) {
		for (var k : map.entrySet())
			pw.println(k.toString().replace("=", ","));
	}
}

