package Esercizio1;

public class Writer implements Runnable {
    private RWbasic rwObject;
    private int id;
    
    public Writer(RWbasic rwObject, int id) {
        this.rwObject = rwObject;
        this.id = id;
    }
    
    @Override
    public void run() {
        System.out.println("Writer " + id + " starting write operation");
        // Simulate some work with a sleep
        try {
            Thread.sleep(100); // Simulate time taken to write
        } catch (InterruptedException e) {
        }
        rwObject.write();
        System.out.println("Writer " + id + " completed write operation");
    }
}
