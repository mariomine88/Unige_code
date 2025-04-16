package Esercizio4;

public class Reader implements Runnable {
    private RWext rwObject;
    private int id;
    
    public Reader(RWext rwObject, int id) {
        this.rwObject = rwObject;
        this.id = id;
    }
    
    @Override
    public void run() {
        int value = rwObject.read();
        System.out.println("Reader " + id + " read value: " + value);
    }
}
