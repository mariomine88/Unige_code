package lab06;

import java.util.Iterator;
import java.util.NoSuchElementException;

class SimpleRangeIterator implements Iterator<Integer> {

	protected int next;
	protected final int end;

	SimpleRangeIterator(int next, int end) {
	    this.next = next;
		this.end = end;
	}

	@Override
	public boolean hasNext() {
	    return next < end;
	}

	@Override
	public Integer next() {
		if (!hasNext()) {
            throw new NoSuchElementException();
        }
        return next++;
	}

}
