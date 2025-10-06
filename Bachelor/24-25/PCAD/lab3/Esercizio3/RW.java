package Esercizio3;

import Esercizio1.RWbasic;

public class RW extends RWbasic {
    private int activeReaders = 0;
    private boolean writerActive = false;
    
    // Metodo per i lettori per iniziare la lettura
    private synchronized void beginRead() throws InterruptedException {
        // Aspetta se c'è uno scrittore attivo
        while (writerActive) {
            wait();
        }
        // Incrementa il contatore dei lettori attivi
        activeReaders++;
    }
    
    // Metodo per i lettori per terminare la lettura
    private synchronized void endRead() {
        // Decrementa il contatore dei lettori attivi
        activeReaders--;
        // Se non ci sono più lettori, notifica tutti i thread in attesa (potenzialmente scrittori)
        if (activeReaders == 0) {
            notifyAll();
        }
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
            // Aspetta finché non ci sono lettori attivi e nessun altro scrittore attivo
            while (activeReaders > 0 || writerActive) {
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
            notifyAll();
        }
    }
}
