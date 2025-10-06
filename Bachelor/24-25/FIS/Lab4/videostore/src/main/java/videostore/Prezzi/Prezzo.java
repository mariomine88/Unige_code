package videostore.Prezzi;

import videostore.Noleggio;

public abstract  class Prezzo {
    
    public abstract  int getCodicePrezzo();

    public abstract double getAmmontare(int giorniNoleggio);
        /*double risultato = 0.0;
        switch (noleggio.getFilm().getCodicePrezzo()) {
        case Film.REGOLARE:
            risultato += 2;
            if (noleggio.getGiorniNoleggio() > 2)
                risultato += (noleggio.getGiorniNoleggio() - 2) * 1.5;
            break;
        case Film.NOVITA:
            risultato += noleggio.getGiorniNoleggio() * 3;
            break;
        default://Film.BAMBINI:
            risultato += 1.5;
            if (noleggio.getGiorniNoleggio() > 3)
                risultato += (noleggio.getGiorniNoleggio() - 3) * 1.5;
            break;
        }
        return risultato;*/
    
}
