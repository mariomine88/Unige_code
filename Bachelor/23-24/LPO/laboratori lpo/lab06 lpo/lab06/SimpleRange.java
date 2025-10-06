package lab06;

public class SimpleRange implements Range {

	protected final int start, end;

	// initializes a range from start (inclusive) to end (exclusive)
	protected SimpleRange(int start, int end) {
        this.start = start;
        this.end = end;
	}

	// returns a range from start (inclusive) to end (exclusive)
	public static SimpleRange withStartEnd(int start, int end) {
		return new SimpleRange(start, end);
	}

	// returns a range from 0 (inclusive) to end (exclusive)
	public static SimpleRange withEnd(int end) {
		return new SimpleRange(0, end);
	}

	// implements the abstract method of Iterable, returns a new SimpleRangeIterator
	@Override
	public SimpleRangeIterator iterator() {
	    return new SimpleRangeIterator(start, end);
	}

}
