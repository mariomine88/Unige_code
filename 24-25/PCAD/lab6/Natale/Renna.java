package Natale;

public class Renna implements Runnable {
    private int id;
    private SantaScenario scenario;

    public Renna(int id, SantaScenario scenario) {
        this.id = id;
        this.scenario = scenario;
    }

    @Override
    public void run() {
        try {
            while (true) {
                // Tempo di vacanza
                System.out.println("La renna " + id + " e in vacanza");
                Thread.sleep(2000 + (long) (Math.random() * 4000)); // Simula il tempo di vacanza
                
                // La renna ritorna dalle vacanze
                System.out.println("La renna " + id + " e tornata dalle vacanze, ora sta aspettando");
                scenario.RennaReturns();
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}