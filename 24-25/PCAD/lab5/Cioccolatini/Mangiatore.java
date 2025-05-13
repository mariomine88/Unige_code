package Cioccolatini;

public class Mangiatore implements Runnable {
    private int id;
    
    public Mangiatore(int id) {
        this.id = id;
    }
    
    @Override
    public void run() {
        try {
            while (true) {
                // Attende che ci sia almeno un cioccolatino disponibile
                ScatolaCioccolatini.cioccolatiniDisponibili.acquire();
                
                // Acquisisce il mutex per accedere alla scatola
                ScatolaCioccolatini.mutex.acquire();
                
                // Prende un cioccolatino
                ScatolaCioccolatini.cioccolatiniNellaScatola--;
                System.out.println("Mangiatore " + id + ": ho preso un cioccolatino. " + 
                                  "Rimasti: " + ScatolaCioccolatini.cioccolatiniNellaScatola);
                
                // Se la scatola è diventata vuota, segnala al pasticciere
                if (ScatolaCioccolatini.cioccolatiniNellaScatola == 0) {
                    System.out.println("Mangiatore " + id + ": ho preso l'ultimo cioccolatino, scatola vuota!");
                    ScatolaCioccolatini.scatolaVuota.release();
                }
                
                // Rilascia il mutex
                ScatolaCioccolatini.mutex.release();
                
                // Simula il tempo necessario per mangiare il cioccolatino
                Thread.sleep(1000);
            }
        } catch (InterruptedException e) {
            System.out.println("Mangiatore " + id + " interrotto");
        }
    }
}