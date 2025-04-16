package Esercizio4;

import Esercizio1.RWbasic;

public class RWext extends RWbasic {
    private int activeReaders = 0;
    private boolean writerActive = false;
    private boolean valueUnread = false;
    
    // Metodo per i lettori per iniziare la lettura
    private synchronized void beginRead() throws InterruptedException {
        // Aspetta solo se c'è uno scrittore attivo
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
        
        // Se questo lettore ha letto un valore non ancora letto, marcalo come letto
        if (valueUnread) {
            valueUnread = false;
            notifyAll(); // Notifica eventuali scrittori in attesa
        }
        
        // Se non ci sono più lettori, notifica tutti i thread in attesa
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
            // Aspetta finché non ci sono lettori attivi, nessun altro scrittore attivo
            // e il valore precedente è stato letto da almeno un lettore
            while (activeReaders > 0 || writerActive || valueUnread) {
                wait();
            }
            
            writerActive = true;
            
            // Esegue l'operazione di scrittura
            super.write();
            
            // Imposta il flag che indica che c'è un nuovo valore non ancora letto
            valueUnread = true;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            // Cancella il flag dello scrittore attivo e notifica i thread in attesa
            writerActive = false;
            notifyAll();
        }
    }
}
