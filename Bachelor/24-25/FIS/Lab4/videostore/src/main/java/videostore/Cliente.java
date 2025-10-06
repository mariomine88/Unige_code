package videostore;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

// 1.0
public class Cliente {
    
        @SuppressWarnings("FieldMayBeFinal")
	private String nome;
    private List<Noleggio> noleggi = new ArrayList<>();

    public Cliente (String nome) {
        this.nome = nome;
    }

    public void addNoleggio(Noleggio arg) {
        noleggi.add(arg);
    }
    
    public String getNome(){
        return nome;
    }

private double getAmmontareTotale() {

    double ammontareTotale = 0;
    for (Noleggio noleggio : noleggi) {
        ammontareTotale += noleggio.getAmmontare();
    }
    return ammontareTotale;
    }

public String rendiconto() {

    Iterator<Noleggio> noleggiIt = noleggi.iterator();
    StringBuilder r = new StringBuilder();
    r.append("Rendiconto noleggi per " + getNome() + ": ");
    
    while (noleggiIt.hasNext()) {
        Noleggio noleggio = noleggiIt.next();
        
        // calcola ammontare per ogni noleggio
        double questoAmmontare = noleggio.getAmmontare();
        
        r.append(noleggio.getFilm().getTitolo())
        .append(" ")
        .append(questoAmmontare)
        .append(" ");
        }
        
        r.append("L'ammontare dovuto e' ").append(getAmmontareTotale());
        return r.toString();
    }
}
