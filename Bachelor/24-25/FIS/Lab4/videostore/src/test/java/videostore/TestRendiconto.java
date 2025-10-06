package videostore;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class TestRendiconto {

	@Test
	public void testVideoStore() {
		Cliente cliente1 = new Cliente("Cliente001");
		
		Film film1 = new Film("Pulp Fiction", 0); // REGOLARE
		Film film2 = new Film("The Substance", 1); // NOVITA'
		Film film3 = new Film("Koda, Fratello Orso", 2); // BAMBINI
		
		Noleggio noleggio1 = new Noleggio(film1 , 3);
		Noleggio noleggio2 = new Noleggio(film2, 5);
		Noleggio noleggio3 = new Noleggio(film3, 7);
		
		cliente1.addNoleggio(noleggio1);
		cliente1.addNoleggio(noleggio2);
		cliente1.addNoleggio(noleggio3);
		
		System.out.println(cliente1.rendiconto());
		
		String res = "Rendiconto noleggi per Cliente001: Pulp Fiction 3.5 The Substance 15.0 Koda, Fratello Orso 7.5 L'ammontare dovuto e' 26.0";
		
		assertEquals("*************\n** test KO **\n*************", cliente1.rendiconto(), res);
		
		if (res.equals(cliente1.rendiconto()))
			System.out.println("=============\n== test OK ==\n=============");
		else
			System.out.println("*************\n** test KO **\n*************");
	}
}
