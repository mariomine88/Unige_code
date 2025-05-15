package Natale;

import java.util.concurrent.Semaphore;

public class SantaScenario {
    // Semafori per la sincronizzazione
    private Semaphore santaSemaphore = new Semaphore(0);
    private Semaphore RennaSemaphore = new Semaphore(0);
    private Semaphore ElfoSemaphore = new Semaphore(0);
    private Semaphore ElfoTurn = new Semaphore(3); 
    private Semaphore elfCanWakeSanta = new Semaphore(1); 
    
    // Mutex per la protezione dei contatori
    private Semaphore mutexElves = new Semaphore(1);
    private Semaphore mutexRenna = new Semaphore(1);
    
    // Contatori
    private int waitingElves = 0;
    private int waitingRenna = 0;

    // Indica se Babbo Natale deve aiutare le renne o gli elfi
    private boolean helpingRenna = false;

    // Babbo Natale aspetta fino a quando non e necessario
    public void santaWait() throws InterruptedException {
        santaSemaphore.acquire();
    }

    // Babbo Natale decide chi aiutare
    public boolean helpRenna() {
        return helpingRenna;
    }

    // Babbo Natale finisce di aiutare le renne
    public void finishHelpingRenna() throws InterruptedException {
        System.out.println("Babbo Natale ha consegnato i regali");
        System.out.println("Babbo Natale ha aiutato le renne");
        // Rilascia tutte le renne per consegnare i regali
        RennaSemaphore.release(9);
        waitingRenna = 0;
        helpingRenna = false;
        elfCanWakeSanta.release();
    }

    // Babbo Natale finisce di aiutare gli elfi
    public void finishHelpingElfi() throws InterruptedException {
        System.out.println("Babbo Natale ha aiutato gli elfi");
        // Rilascia gli elfi
        ElfoSemaphore.release(3);
        waitingElves -= 3;
        ElfoTurn.release(3); // Consenti al prossimo gruppo di elfi
        elfCanWakeSanta.release();
    }

    // La renna ritorna dalle vacanze
    public void RennaReturns() throws InterruptedException {
        mutexRenna.acquire();
        waitingRenna++;
        
        if (waitingRenna == 9) {
            System.out.println("Tutte le renne sono tornate! Svegliamo Babbo Natale");
            elfCanWakeSanta.acquire();
            helpingRenna = true;
            santaSemaphore.release();
        }
        mutexRenna.release();
        
        // Aspetta che Babbo Natale aiuti con la slitta
        RennaSemaphore.acquire();
    }

    // L'elfo ha bisogno di aiuto
    public void ElfoNeedsHelp(int id) throws InterruptedException {
        ElfoTurn.acquire(); // Solo 3 elfi alla volta possono richiedere aiuto
        
        mutexElves.acquire();
        waitingElves++;
        
        if (waitingElves == 3) {
            // Se tutte le renne non sono tornate, sveglia Babbo Natale
            elfCanWakeSanta.acquire();
            System.out.println("Tre elfi stanno svegliando Babbo Natale!");
            santaSemaphore.release();
        }
        mutexElves.release();
        
        // Aspetta l'aiuto di Babbo Natale
        ElfoSemaphore.acquire();
        System.out.println("L'elfo " + id + " e stato aiutato da Babbo Natale");
    }
}