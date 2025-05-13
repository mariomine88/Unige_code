package piscina;
import java.util.concurrent.Semaphore;

public class PoolSimulation {
    public static void main(String[] args) {
        // Configurazione della simulazione
        int numClients = 20;   // Numero di clienti
        int NS = 5;            // Numero di spogliatoi
        int NC = 5;            // Numero di armadietti
        
        // Creare i semafori per spogliatoi e armadietti
        Semaphore spogliatoi = new Semaphore(NS);
        Semaphore armadietti = new Semaphore(NC);
        
        System.out.println("Simulazione piscina con " + NS + " spogliatoi e " + NC + " armadietti");
        System.out.println("Numero di clienti: " + numClients);
        
        // Creare e avviare i thread dei clienti
        for (int i = 1; i <= numClients; i++) {
            new ClienteMigliorato(i, spogliatoi, armadietti).start();
            // Piccolo ritardo tra l'arrivo di ogni cliente
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}