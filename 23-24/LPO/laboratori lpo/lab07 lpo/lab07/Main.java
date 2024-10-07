package lab07;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

public class Main {
	// class fields for managing options
	private static final String INPUT_OPT = "-i";
	private static final String OUTPUT_OPT = "-o";
	private static final String SORTED_OPT = "-sort";

	/*
	 * options with no argument are initially mapped to null, 
	 * when they are set they
	 * are mapped to a String array of length 0 options with one argument are mapped
	 * to a String array of length 1 initially containing null
	 */
	private static final Map<String, String[]> options = new HashMap<>();
	static {
		options.put(INPUT_OPT, new String[1]); // one argument, initially null
		options.put(OUTPUT_OPT, new String[1]); // one argument, initially null
		options.put(SORTED_OPT, null); // no arguments, option not set by default
	}

	// prints 'msg' on the standard error and exits with status code 1
	private static void error(String msg) {
		System.err.println(msg);
		System.exit(1);
	}

	// processes all options and their arguments, if any
	private static void processArgs(String[] args) {
		for (var i = 0; i < args.length; i++) {
			var opt = args[i];
			if (!options.containsKey(opt))
				error("Option error.\nValid options:\n\t-i <input>\n\t-o <output>\n\t-sort");
			var val = options.get(opt);
			if (val == null) // option with no argument, not set yet
				options.put(opt, new String[0]); // sets the option
			else if (val.length > 0) // option with one argument
			{
				if (i + 1 == args.length)
					error("Missing argument for option " + opt);
				val[0] = args[++i];
			}
		}
	}

	// tries to open the input stream or the standard input 
	// if 'inputPath' is null returns a buffered reader associated with the standard input
	// throws FileNotFoundException if 'inputPath' is not null but the file cannot be opened
	private static BufferedReader tryOpenInput(String inputPath) throws FileNotFoundException {
		return new BufferedReader(inputPath == null ? new InputStreamReader(System.in) : new FileReader(inputPath));
	}

	// tries to open the output stream or the standard output 
	// if 'outputPath' is null, then returns a print writer associated with the standard output
	// throws FileNotFoundException if 'outputPath' is not null but the file cannot be opened
	private static PrintWriter tryOpenOutput(String outputPath) throws FileNotFoundException {
		return outputPath == null ? new PrintWriter(System.out) : new PrintWriter(outputPath);
	}

	public static void main(String[] args) {
		// processes the arguments
		// manages streams and exceptions with try-with-resources
		// calls method 'sumScoresGroupById' of 'CsvUtilities'
		// passes an empty hash map if flag '-sort' is not set
		// otherwise passes an empty tree map initialized with a 'ComparePersonBySurname' comparator
		// prints the map by calling method 'print' of 'CsvUtilities'
		processArgs(args); 
		try (var rd = tryOpenInput(options.get(INPUT_OPT)[0]); var pw = tryOpenOutput(options.get(OUTPUT_OPT)[0]);) {
			Map<Person, Integer> output;
			if (options.get(SORTED_OPT) != null) // the output must be sorted
				output = new TreeMap<>(new ComparePersonBySurname());
			else
				output = new HashMap<>();
			var csv = new CsvUtilitiesClass();
			csv.sumScoresGroupById(rd, output);
			csv.print(output, pw);
		} catch (FileNotFoundException e) {
			error("I/O error: " + e.getMessage());
		} catch (RuntimeException e) {
			error("Input format error");
		} catch (Throwable t) {
			error("Unexpected error");
			t.printStackTrace();
		}
	}

}
