package lab04;
 
 // confronta le figure basandosi sulle loro aree

public class AreaComparator implements ShapeComparator {

	//@ requires: shape1 != null && shape2 != null
	
	public int compare(Shape shape1, Shape shape2) {
		if (shape1 == null || shape2 == null) {
			throw new NullPointerException("shape1 and shape2 must be not null");
		}
		if (shape1.area() > shape2.area()) {
			return 1;
		} else if (shape1.area() < shape2.area()) {
			return -1;
		} else {
			return 0;
		}
	}

}
