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
                Thread.sleep(4000);
                
                // La renna ritorna dalle vacanze
                System.out.println("La renna " + id + " e tornata dalle vacanze, ora sta aspettando");
                scenario.RennaReturns();
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}