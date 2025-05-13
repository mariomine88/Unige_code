package piscina;


import java.util.concurrent.Semaphore;

class ClienteMigliorato extends Thread {
    private int id;
    private Semaphore spogliatoi;
    private Semaphore armadietti;
    
    public ClienteMigliorato(int id, Semaphore spogliatoi, Semaphore armadietti) {
        this.id = id;
        this.spogliatoi = spogliatoi;
        this.armadietti = armadietti;
    }
    
    @Override
    public void run() {
        try {
            System.out.println("Cliente " + id + ": e arrivato alla piscina");
            
            // MODIFICA: Prende entrambe le chiavi insieme o nessuna
            // Questo previene il deadlock
            System.out.println("Cliente " + id + ": attende spogliatoio e armadietto");
            
            // Usa tryAcquire per tentare di acquisire uno spogliatoio
            if (spogliatoi.tryAcquire()) {
                System.out.println("Cliente " + id + ": ha preso la chiave di uno spogliatoio");
                
                // Prova a prendere un armadietto entro un timeout
                if (armadietti.tryAcquire(1000, java.util.concurrent.TimeUnit.MILLISECONDS)) {
                    // Ha entrambe le risorse, può procedere
                    System.out.println("Cliente " + id + ": ha preso la chiave di un armadietto");
                    
                    // c) Si cambia nello spogliatoio
                    System.out.println("Cliente " + id + ": si sta cambiando");
                    Thread.sleep(500);
                    
                    //d) Rida la chiave dello spogliatoio
                    System.out.println("Cliente " + id + ": rida la chiave dello spogliatoio");
                    spogliatoi.release();
                    
                    // g) Nuota (tenendosi la chiave dell'armadietto)
                    System.out.println("Cliente " + id + ": sta nuotando");
                    Thread.sleep(2000);
                    
                    // h) Prende la chiave di uno spogliatoio
                    System.out.println("Cliente " + id + ": attende uno spogliatoio");
                    spogliatoi.acquire();
                    System.out.println("Cliente " + id + ": ha preso la chiave di uno spogliatoio");
                    
                    // i) Ricupera i suoi vestiti nell'armadietto
                    System.out.println("Cliente " + id + ": recupera i vestiti dall'armadietto");
                    Thread.sleep(300);
                    
                    // j) Si riveste nello spogliatoio
                    System.out.println("Cliente " + id + ": si sta rivestendo");
                    Thread.sleep( 1500);
                    
                    // k) Libera lo spogliatoio
                    System.out.println("Cliente " + id + ": ha finito di cambiarsi");
                    
                    // l) Rida le chiavi dello spogliatoio e dell'armadietto
                    System.out.println("Cliente " + id + ": rida le chiavi dello spogliatoio e dell'armadietto");
                    spogliatoi.release();
                    armadietti.release();
                    
                    System.out.println("Cliente " + id + ": ha lasciato la piscina");
                } else {
                    // Non può ottenere un armadietto, rilascia lo spogliatoio e riprova
                    System.out.println("Cliente " + id + ": non ha trovato armadietti liberi, rilascia lo spogliatoio");
                    spogliatoi.release();
                    // Attende un po' prima di riprovare
                    Thread.sleep(500);
                    run(); // Riprova
                    return;
                }
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}