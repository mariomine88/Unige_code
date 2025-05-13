package Cioccolatini;

public class Pasticciere implements Runnable {
    @Override
    public void run() {
        try {
            while (true) {
                // Attende che la scatola sia vuota
                ScatolaCioccolatini.scatolaVuota.acquire();
                
                // Acquisisce il mutex per accedere alla scatola
                ScatolaCioccolatini.mutex.acquire();
                
                // Riempie la scatola con P cioccolatini
                ScatolaCioccolatini.cioccolatiniNellaScatola = ScatolaCioccolatini.P;
                System.out.println("Pasticciere: ho riempito la scatola con " + 
                                   ScatolaCioccolatini.P + " cioccolatini");
                
                // Rilascia P permessi per i cioccolatini disponibili
                ScatolaCioccolatini.cioccolatiniDisponibili.release(ScatolaCioccolatini.P);
                
                // Rilascia il mutex
                ScatolaCioccolatini.mutex.release();
            }
        } catch (InterruptedException e) {
            System.out.println("Pasticciere interrotto");
        }
    }
}