package Esercizio3;

public class Esercizio3 {
    public static void main(String[] args) {
        RW rwObject = new RW();
        
        int numThreads = 50;
        Thread[] readers = new Thread[numThreads];
        Thread[] writers = new Thread[numThreads];
        
        // Create and start writer threads
        for (int i = 0; i < numThreads; i++) {
            writers[i] = new Thread(new Writer(rwObject, i));
            writers[i].start();
        }
        
        // Create and start reader threads
        for (int i = 0; i < numThreads; i++) {
            readers[i] = new Thread(new Reader(rwObject, i));
            readers[i].start();
        }
        
        // Wait for all writers to finish
        for (int i = 0; i < numThreads; i++) {
            try {
                writers[i].join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        
        // Wait for all readers to finish
        for (int i = 0; i < numThreads; i++) {
            try {
                readers[i].join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        
        // Print final result
        System.out.println("Final value of data: " + rwObject.read());
        System.out.println("Expected value: " + numThreads);
        System.out.println("Difference due to race conditions: " + 
                          (numThreads - rwObject.read()));
    }
}
