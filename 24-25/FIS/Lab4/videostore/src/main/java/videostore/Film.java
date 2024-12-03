package videostore;

// 1.0
public class Film {
    
	public static final int BAMBINI = 2;
    public static final int REGOLARE = 0;
    public static final int NOVITA = 1;
    
    private String titolo;
    private int codicePrezzo;

    public Film(String titolo, int codicePrezzo) {
        this.titolo = titolo;
        this.codicePrezzo = codicePrezzo;
    }

    public int getCodicePrezzo() {
        return codicePrezzo;
    }

    public void setCodicePrezzo(int codicePrezzo) {
        this.codicePrezzo = codicePrezzo;
    }

    public String getTitolo() {
        return titolo;
    }

    double getAmmontare(Noleggio noleggio) {
        double risultato = 0.0;
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
        return risultato;
    }
}
