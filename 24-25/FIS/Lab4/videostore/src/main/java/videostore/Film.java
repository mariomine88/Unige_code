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
}
