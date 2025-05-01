package server;
import java.util.LinkedList;
import java.util.Queue;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class StringQueue {
    private final Queue<String> queue = new LinkedList<>();
    private final Lock lock = new ReentrantLock();
    private final Condition notEmpty = lock.newCondition();
    private final Condition notFull = lock.newCondition();
    private final int capacity;
    private final boolean limited;

    // Unlimited queue constructor
    public StringQueue() {
        this.capacity = Integer.MAX_VALUE;
        this.limited = false;
    }

    // Limited queue constructor
    public StringQueue(int capacity) {
        this.capacity = capacity;
        this.limited = true;
    }

    public void add(String message) throws InterruptedException {
        lock.lock();
        try {
            while (limited && queue.size() >= capacity) {
                notFull.await(); // Wait until there is space
            }
            queue.add(message);
            notEmpty.signal(); // Signal that queue is not empty
        } finally {
            lock.unlock();
        }
    }

    public String remove() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) {
                notEmpty.await(); // Wait until there is at least one element
            }
            String message = queue.remove();
            if (limited) {
                notFull.signal(); // Signal that queue is not full
            }
            return message;
        } finally {
            lock.unlock();
        }
    }
}