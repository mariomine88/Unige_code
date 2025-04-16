package Esercizio1;

public class Reader implements Runnable {
    private RWbasic rwObject;
    private int id;
    
    public Reader(RWbasic rwObject, int id) {
        this.rwObject = rwObject;
        this.id = id;
    }
    
    @Override
    public void run() {
        int value = rwObject.read();
        System.out.println("Reader " + id + " read value: " + value);
    }
}
