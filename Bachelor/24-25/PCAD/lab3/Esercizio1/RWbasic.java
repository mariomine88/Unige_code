package Esercizio1;
public class RWbasic {
    private int data = 0;
    
    public int read() {
        return data;
    }
    
    public void write() {
        int tmp = data;         // (a): mette il valore di data in una variabile temporanea tmp
        tmp = tmp + 1;          // (b): aumenta di 1 il valore di tmp
        data = tmp;             // (c): mette il valore di tmp in data
    }
}
