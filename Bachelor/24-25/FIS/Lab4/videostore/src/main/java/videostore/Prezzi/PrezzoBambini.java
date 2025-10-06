package videostore.Prezzi;

import videostore.Film;

public class PrezzoBambini extends Prezzo {
    
    @Override
    public int getCodicePrezzo() {
        return Film.BAMBINI;
    }
    @Override
    public double getAmmontare(int giorniNoleggio) {
        double risultato = 1.5;
            if (giorniNoleggio> 3)
                risultato += (giorniNoleggio - 3) * 1.5;
        return risultato;
    }
}