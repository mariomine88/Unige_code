package Esercizio4;

import Esercizio1.RWbasic;

public class RWext extends RWbasic {
    private int activeReaders = 0;
    private boolean writerActive = false;
    private boolean valueUnread = false;
    
    // Metodo per i lettori per iniziare la lettura
    private synchronized void beginRead() throws InterruptedException {
        // Aspetta se c'è uno scrittore attivo
        while (writerActive || !valueUnread) {
            wait();
        }
        // Incrementa il contatore dei lettori attivi
        activeReaders++;
    }
    
    // Metodo per i lettori per terminare la lettura
    private synchronized void endRead() {
        // Decrementa il contatore dei lettori attivi
        activeReaders--;
        valueUnread = false;
        notifyAll();
    }
    
    // Ridefinizione del metodo read per utilizzare il pattern begin/end
    @Override
    public int read() {
        int value = 0;
        try {
            beginRead();
            value = super.read(); // Operazione di lettura effettiva
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            endRead();
        }
        return value;
    }
    
    // Gli scrittori necessitano di accesso esclusivo
    @Override
    public synchronized void write() {
        try {
            // Aspetta finché non ci sono lettori attivi, nessun altro scrittore attivo
            // e il valore precedente è stato letto da almeno un lettore
            while (activeReaders > 0 || writerActive || valueUnread) {
                wait();
            }
            // Imposta il flag dello scrittore attivo
            writerActive = true;
            
            // Esegue l'operazione di scrittura
            super.write();

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            // Cancella il flag dello scrittore attivo e notifica i thread in attesa
            writerActive = false;
            valueUnread = true; // Marca il valore come non ancora letto
            notifyAll();
        }
    }
}
