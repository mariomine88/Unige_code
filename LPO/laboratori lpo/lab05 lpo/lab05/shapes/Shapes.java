package lab05.shapes;

public class Shapes {

	/*
	 * restituisce 
	 * - la prima figura maggiore o uguale alle altre in shapes rispetto al comparator comp 
	 * - null se shapes e` vuoto
	 * assume che l'ordine sia totale
	 *@ requires: shapes != null && comp != null 
	 */
	public static Shape max(Shape[] shapes, ShapeComparator comp) {
		if (comp == null)
			throw new NullPointerException();
		if (shapes.length == 0)
			return null;
		Shape res = shapes[0];
		for (int i = 1; i < shapes.length; i++) {
			Shape s = shapes[i];
			if (comp.compare(s, res) > 0) // la figura corrente s è maggiore
				res = s;
		}
		return res;
	}

	/*
	 * muove tutte le figure in shapes lungo il vettore (dx,dy) 
	 *@ requires: shapes != null
	 */
	
	public static void moveAll(Shape[] shapes, double dx, double dy) {
		for (Shape s : shapes)
			s.move(dx, dy);
	}

	/*
	 * scala tutte le figure in shapes del fattore factor, senza muovere il loro centro
	 *@ requires shapes != null && factor > 0
	 */
	
	public static void scaleAll(Shape[] shapes, double factor) {
		if (factor <= 0)
			throw new IllegalArgumentException();
		for (Shape s : shapes)
			s.scale(factor);
	}

	/*
	 * restituisce la somma delle aree di tutte le figure in shapes 
	 *@ requires shapes != null
	 */
	
	public static double totalArea(Shape[] shapes) {
		double res = 0;
		for (Shape s : shapes)
			res += s.area();
		return res;
	}


}
