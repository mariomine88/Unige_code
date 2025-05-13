package piscina;
import java.util.concurrent.Semaphore;

class Cliente extends Thread {
    private int id;
    private Semaphore spogliatoi;
    private Semaphore armadietti;
    
    public Cliente(int id, Semaphore spogliatoi, Semaphore armadietti) {
        this.id = id;
        this.spogliatoi = spogliatoi;
        this.armadietti = armadietti;
    }
    
    @Override
    public void run() {
        try {
            System.out.println("Cliente " + id + ": e arrivato alla piscina");
            
            // a) Prende la chiave di uno spogliatoio
            System.out.println("Cliente " + id + ": attende uno spogliatoio");
            spogliatoi.acquire();
            System.out.println("Cliente " + id + ": ha preso la chiave di uno spogliatoio");
            
            // b) Prende la chiave di un armadietto
            System.out.println("Cliente " + id + ": attende un armadietto");
            armadietti.acquire();
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
            
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}