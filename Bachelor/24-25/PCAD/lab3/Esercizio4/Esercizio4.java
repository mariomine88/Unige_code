package Esercizio4;
public class Esercizio4 {
    public static void main(String[] args) {
        RWext rwObject = new RWext();
        
        int readersThreads = 70;
        int writersThreads = 50;
        Thread[] readers = new Thread[readersThreads];
        Thread[] writers = new Thread[writersThreads];
        
        // Create and start writer threads
        for (int i = 0; i < writersThreads; i++) {
            writers[i] = new Thread(new Writer(rwObject, i));
            writers[i].start();
        }

        // Create and start reader threads
        for (int i = 0; i < readersThreads; i++) {
            readers[i] = new Thread(new Reader(rwObject, i));
            readers[i].start();
        }
        
        // Wait for all writers to finish
        for (int i = 0; i < writersThreads; i++) {
            try {
                writers[i].join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        
        // Wait for all readers to finish
        for (int i = 0; i < readersThreads; i++) {
            try {
                readers[i].join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        
        // Print final result
        System.out.println("Final value of data: " + rwObject.read());
        System.out.println("Expected value: " + writersThreads);
        System.out.println("Difference due to race conditions: " + 
                          (writersThreads - rwObject.read()));
    }
}
