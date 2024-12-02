package videostore;
import java.util.*;

// 1.0
public class Cliente {
    
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

    public String rendiconto() {
       
    	double ammontareTotale = 0;
        Iterator<Noleggio> noleggiIt = noleggi.iterator();
        StringBuilder r = new StringBuilder();
        r.append("Rendiconto noleggi per " + getNome() + ": ");
        
        while (noleggiIt.hasNext()) {
            double questoAmmontare = 0;
            Noleggio noleggio = noleggiIt.next();
            
            // calcola ammontare per ogni noleggio
            switch (noleggio.getFilm().getCodicePrezzo()) {
            case Film.REGOLARE:
                questoAmmontare += 2;
                if (noleggio.getGiorniNoleggio() > 2)
                    questoAmmontare += (noleggio.getGiorniNoleggio() - 2) * 1.5;
                break;
            case Film.NOVITA:
                questoAmmontare += noleggio.getGiorniNoleggio() * 3;
                break;
            default://Film.BAMBINI:
                questoAmmontare += 1.5;
                if (noleggio.getGiorniNoleggio() > 3)
                    questoAmmontare += (noleggio.getGiorniNoleggio() - 3) * 1.5;
                break;
            }
            ammontareTotale += questoAmmontare;

            r.append(noleggio.getFilm().getTitolo())
            .append(" ")
            .append(questoAmmontare)
            .append(" ");   
            
        }

        r.append("L'ammontare dovuto e' ").append(ammontareTotale);
        return r.toString();
    }
}
