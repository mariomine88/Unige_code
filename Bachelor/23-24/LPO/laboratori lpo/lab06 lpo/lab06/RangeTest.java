package lab06;

import java.util.Iterator;

public class RangeTest {

	public static void main(String[] args) {
		Range r = SimpleRange.withStartEnd(2, 2);
		for (int x : r) // prints no elements
			System.out.println(x);
		
		System.out.println("=======");

		r = SimpleRange.withEnd(3);
		for (int x : r)
			for (int y : r)
				System.out.println(x + " " + y);
        
		/* prints
	     * 0 0
	     * 0 1
	     * 0 2
	     * 1 0
	     * 1 1
	     * 1 2
	     * 2 0
	     * 2 1
	     * 2 2
	     */
        
		System.out.println("=======");

		// same test with while and explicit iterators

		Iterator<Integer> it1 = r.iterator();
		while (it1.hasNext()) {
			int x = it1.next();
			
			Iterator<Integer> it2 = r.iterator();
			while (it2.hasNext())
				System.out.println(x + " " + it2.next());
		}
		
		System.out.println("=======");

		// tests with StepRange
		
		r = StepRange.withStartEndStep(1, 5, 2);
		for (int x : r) // prints no elements
			System.out.print(x+" "); // prints 1 3
		
		System.out.println();
		System.out.println("=======");
		
		r = StepRange.withStartEndStep(5, 1, -2);
		for (int x : r) // prints no elements
			System.out.print(x+" "); // prints 1 3
		
	}
}
