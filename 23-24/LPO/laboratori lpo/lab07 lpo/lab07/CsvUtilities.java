package lab07;

import java.io.PrintWriter;
import java.util.Map;

public interface CsvUtilities {

	// reads from 'readable' a table in CSV format of 'Person' objects associated with 'score' 
	// groups by 'id', converts 'name' and 'surname' into upper case, and sums 'score' 
	// outputs the result in the dictionary 'output' where keys are 'Person' objects, and values their final 'Integer' 'score' 
	// may throw java.util.NoSuchElementException if some expected data are missing
	// or java.util.InputMismatchException or java.lang.IllegalArgumentException if some data does not match the expected type
	// additional columns are tacitly ignored
	void sumScoresGroupById(Readable readable, Map<Person, Integer> output);

	// writes a generic map into CSV format by using pw
	// if keys and values are structured, 
	// then columns are generated for all printable fields as defined by the corresponding 'toString()' method
	// key fields are printed prior to value fields
	<K, V> void print(Map<K, V> map, PrintWriter pw);
}
