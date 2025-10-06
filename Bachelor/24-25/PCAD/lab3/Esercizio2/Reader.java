package Esercizio2;

public class Reader implements Runnable {
    private RWexclusive rwObject;
    private int id;
    
    public Reader(RWexclusive rwObject, int id) {
        this.rwObject = rwObject;
        this.id = id;
    }
    
    @Override
    public void run() {
        int value = rwObject.read();
        System.out.println("Reader " + id + " read value: " + value);
    }
}
