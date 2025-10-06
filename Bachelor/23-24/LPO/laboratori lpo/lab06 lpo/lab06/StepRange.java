package lab06;

/*
 *@ invariant: step != 0
 */

public class StepRange extends SimpleRange {
 
	protected final int step;	

	protected static int checkStep(int step) {
		if (step == 0)
			throw new IllegalArgumentException("Step cannot be 0");
		return step;
	}

        // initializes a range from start (inclusive) to end (exclusive) with arbitrary step
	protected StepRange(int start, int end, int step) {
		super(start, end);
		this.step = checkStep(step);
	}

	// returns a range from start (inclusive) to end (exclusive) with arbitrary step
	public static StepRange withStartEndStep(int start, int end, int step) {
        return new StepRange(start, end, step);
	}

	// returns a range from start (inclusive) to end (exclusive) with step 1
	public static StepRange withStartEnd(int start, int end) {
		return new StepRange(start, end, 1);
	}

	// returns a range from 0 (inclusive) to end (exclusive) with step 1
	public static SimpleRange withEnd(int end) {
		return new StepRange(0, end, 1);
	}

	// implements the abstract method of Iterable, returns a new StepRangeIterator
	@Override
	public StepRangeIterator iterator() {
        return new StepRangeIterator(start, end, step);
	}

}
