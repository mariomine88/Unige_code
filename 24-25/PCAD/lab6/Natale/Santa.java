package Natale;

public class Santa implements Runnable {
    private SantaScenario scenario;

    public Santa(SantaScenario scenario) {
        this.scenario = scenario;
    }

    @Override
    public void run() {
        try {
            while (true) {
                // Babbo Natale dorme finché non viene svegliato
                scenario.santaWait();
                
                System.out.println("Babbo Natale si e svegliato!");
                
                if (scenario.helpRenna()) {
                    // Aiuta le renne a preparare la slitta
                    System.out.println("Babbo Natale sta preparando la slitta con le renne");
                    Thread.sleep(1000); // Tempo per preparare la slitta
                    System.out.println("I regali sono stati consegnati!");
                } else {
                    // Aiuta gli elfi con i loro problemi di fabbricazione di giocattoli
                    System.out.println("Babbo Natale sta aiutando gli elfi");
                    Thread.sleep(1000); // Tempo per aiutare gli elfi
                }
                
                // Finisce di aiutare e torna a dormire
                scenario.finishHelping();
                System.out.println("Babbo Natale e tornato a dormire");
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}