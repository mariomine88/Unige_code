package lab04;

// definisce metodi di classe di utilità su array di shapes

public class Shapes {

	/*
	 * restituisce 
	 * - la prima figura maggiore o uguale alle altre in shapes rispetto al comparator comp 
	 * - null se shapes e` vuoto
	 * assume che l'ordine sia totale
	 *@ requires: shapes != null && comp != null 
	 */
	public static Shape max(Shape[] shapes, ShapeComparator comp) {
		if (shapes == null || comp == null) {
			throw new NullPointerException("shapes and comp must be not null");
		}
		if (shapes.length == 0) {
			return null;
		}

		//verificate queste due condizioni posso cercare la shape più grande
		Shape max = shapes[0]; //inizializzo la shape più grande alla prima shape dell'array
		//scorro l'array e confronto la shape più grande con le altre, se trovo una shape
		//in cui comp.compare ritorna 1 allora quella shape diventa la più grande,altrimenti nulla 
		for (int i = 1; i < shapes.length; i++) {
			if (comp.compare(max, shapes[i]) < 0) {
				max = shapes[i];
			}
		}
		return max;
	}

	/*
	 * muove tutte le figure in shapes lungo il vettore (dx,dy) 
	 *@ requires: shapes != null
	 */
	
	public static void moveAll(Shape[] shapes, double dx, double dy) {
		if (shapes == null) {
			throw new NullPointerException("shapes must be not null");
		}
		for (int i = 0; i < shapes.length; i++) {
			shapes[i].move(dx, dy);
		}
	}

	/*
	 * scala tutte le figure in shapes del fattore factor, senza muovere il loro centro
	 *@ requires shapes != null && factor > 0
	 */
	
	public static void scaleAll(Shape[] shapes, double factor) {
		if (shapes == null || factor <= 0) {
			throw new IllegalArgumentException("shapes must be not null and factor must be positive");
		}
		for (int i = 0; i < shapes.length; i++) {
			shapes[i].scale(factor);
		}
	}

	/*
	 * restituisce la somma delle aree di tutte le figure in shapes 
	 *@ requires shapes != null
	 */
	
	public static double totalArea(Shape[] shapes) {
		if (shapes == null) {
			throw new NullPointerException("shapes must be not null");
		}
		double totArea = 0;
		for (int i = 0; i < shapes.length; i++) {
			totArea = totArea + shapes[i].area();
		}
		return totArea;
	}

}
