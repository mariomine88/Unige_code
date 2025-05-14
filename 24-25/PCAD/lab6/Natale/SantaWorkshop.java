package Natale;

public class SantaWorkshop {
    private static final int NUM_Renna  = 9;
    private static final int NUM_ELVES = 4;

    public static void main(String[] args) {
        // creamo la classe Scenario
        SantaScenario scenario = new SantaScenario();

        // Inizializziamo Santa
        Thread santaThread = new Thread(new Santa(scenario));
        santaThread.start();

        // Inizializziamo le renne
        for (int i = 0; i < NUM_Renna; i++) {
            Thread RennaThread = new Thread(new Renna(i, scenario));
            RennaThread.start();
        }

        // Inizializziamo gli elfi
        for (int i = 0; i < NUM_ELVES; i++) {
            Thread ElfoThread = new Thread(new Elfo(i, scenario));
            ElfoThread.start();
        }
    }
}