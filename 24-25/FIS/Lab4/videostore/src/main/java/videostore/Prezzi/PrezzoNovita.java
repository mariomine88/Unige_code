package videostore.Prezzi;

import videostore.Film;

public class PrezzoNovita extends Prezzo{
    
    @Override
    public int getCodicePrezzo() {
        return Film.NOVITA;
    }
    @Override
    public double getAmmontare(int giorniNoleggio) {
        double risultato = giorniNoleggio * 3;
        return risultato;
    }
}
