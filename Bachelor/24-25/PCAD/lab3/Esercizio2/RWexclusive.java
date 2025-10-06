package Esercizio2;

import Esercizio1.RWbasic;

public class RWexclusive extends RWbasic {
    @Override
    public synchronized int read() {
        return super.read();
    }
    
    @Override
    public synchronized void write() {
        super.write();
    }
}
