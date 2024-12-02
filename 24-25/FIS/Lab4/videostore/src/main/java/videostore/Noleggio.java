package videostore;

// 1.0
public class Noleggio {
    
	private Film film;
    private int giorniNoleggio;

    public Noleggio(Film film, int giorniNoleggio) {
        this.film = film;
        this.giorniNoleggio = giorniNoleggio;
    }

    public int getGiorniNoleggio() {
        return giorniNoleggio;
    }

    public Film getFilm() {
        return film;
    }
}
