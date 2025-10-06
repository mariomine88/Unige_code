package Esercizio3;

public class Reader implements Runnable {
    private RW rwObject;
    private int id;
    
    public Reader(RW rwObject, int id) {
        this.rwObject = rwObject;
        this.id = id;
    }
    
    @Override
    public void run() {
        int value = rwObject.read();
        System.out.println("Reader " + id + " read value: " + value);
    }
}
