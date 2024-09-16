package lab06;

import java.util.NoSuchElementException;

class StepRangeIterator extends SimpleRangeIterator {

	private final int step;

	StepRangeIterator(int next, int end, int step) {
	    super(next, end);
        if (step == 0) {
            throw new IllegalArgumentException("Step cannot be zero");
        }
        this.step = step;
	}

	@Override
	public boolean hasNext() {
		return step > 0 ? next < end : next > end;
	}

	@Override
	public Integer next() {
        if (!hasNext()) {
            throw new NoSuchElementException();
        }
        int current = next;
        next += step;
        return current;
	}
}
