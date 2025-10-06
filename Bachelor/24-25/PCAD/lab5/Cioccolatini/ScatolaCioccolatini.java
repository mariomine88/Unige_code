package Cioccolatini;
import java.util.concurrent.Semaphore;

public class ScatolaCioccolatini {
    public static final int P = 5; // Capacità massima della scatola
    public static final int NUM_MANGIATORI = 3; // Numero di mangiatori
    
    public static Semaphore mutex = new Semaphore(1); // Per accesso esclusivo alla scatola
    public static Semaphore cioccolatiniDisponibili = new Semaphore(0); // Cioccolatini disponibili
    public static Semaphore scatolaVuota = new Semaphore(1); // Segnala che la scatola è vuota
    
    public static int cioccolatiniNellaScatola = 0; // Contatore dei cioccolatini
    
    public static void main(String[] args) {
        // Crea e avvia il thread del pasticciere
        Thread pasticciere = new Thread(new Pasticciere());
        pasticciere.start();
        
        // Crea e avvia i thread dei mangiatori
        for (int i = 1; i <= NUM_MANGIATORI; i++) {
            Thread mangiatore = new Thread(new Mangiatore(i));
            mangiatore.start();
        }
    }
}