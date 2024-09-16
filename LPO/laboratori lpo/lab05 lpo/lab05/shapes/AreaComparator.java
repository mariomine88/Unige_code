package lab05.shapes;


 // confronta le figure basandosi sulle loro aree

public class AreaComparator implements ShapeComparator {

	//@ requires: shape1 != null && shape2 != null
	
	public int compare(Shape shape1, Shape shape2) {
		double area1 = shape1.area();
		double area2 = shape2.area();
		return area1 > area2 ? 1 : area1 > area2 ? -1 : 0;
	}

}
