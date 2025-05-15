package Natale;

public class Elfo implements Runnable {
    private int id;
    private SantaScenario scenario;

    public Elfo(int id, SantaScenario scenario) {
        this.id = id;
        this.scenario = scenario;
    }

    @Override
    public void run() {
        try {
            while (true) {
                // Lavoro sui giocattoli
                System.out.println("L'elfo " + id + " sta costruendo giocattoli");
                Thread.sleep(2000);
                
                // L'elfo incontra un problema
                System.out.println("L'elfo " + id + " ha bisogno dell'aiuto di Babbo Natale");
                
                // Ottieni aiuto da Babbo Natale
                scenario.ElfoNeedsHelp(id);
                
                // Essere aiutato da Babbo Natale
                Thread.sleep(5000);
                
                // Terminato di ricevere aiuto
                scenario.ElfoGetsHelp(id);
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}