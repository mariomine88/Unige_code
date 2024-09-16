package lab05.shapes;

public class ShapeTest {

	private static void checkAll(Shape[] shapes, Point[] centers, double totalArea, Shape max) {
		for (int i = 0; i < shapes.length; i++)
			assert shapes[i].getCenter().overlaps(centers[i]);
		assert Shapes.totalArea(shapes) == totalArea;
		assert Shapes.max(shapes, new AreaComparator()) == max;
	}

	public static void main(String[] args) {
		Shape s1 = Circle.ofRadiusCenter(2, new PointClass(1, 1));
		Shape s2 = new Circle();
		Shape s3 = Rectangle.ofWidthHeightCenter(1, 2, new PointClass(2, 2));
		Shape[] shapes = { s1, s2, s3 };
		Point[] centers = new Point[shapes.length];
		double totalArea = Shapes.totalArea(shapes);
		Shapes.moveAll(shapes, -1, -1);
		for (int i = 0; i < centers.length; i++)
			centers[i] = shapes[i].getCenter();
		ShapeTest.checkAll(shapes, centers, totalArea, s1);
		Shapes.scaleAll(shapes, .5); // non deve spostare i centri delle figure!
		ShapeTest.checkAll(shapes, centers, totalArea * .25, s1);
		for (Shape s : shapes)
			s.getCenter().move(1, 1); // non deve spostare le figure!
		ShapeTest.checkAll(shapes, centers, totalArea * .25, s1);
	}


}
