package lab05.shapes;

public interface ShapeComparator {
	
	/*
	 * confronta shape1 con shape2
	 * restituisce 
	 * - un numero positivo  se shape1 è maggiore di shape2 
	 * - numero negativo se shape1 è minore di shape2
	 * - 0 altrimenti 
	 */
	
	//@ requires: shape1 != null && shape2 != null

	int compare(Shape shape1, Shape shape2);
}

