package lab05.shapes;

public abstract class AbstractShape implements Shape {

	private final Point center = new PointClass();

	public static final double defaultSize = 1;

	protected static double requirePositive(double size) {
		if (size <= 0)
			throw new IllegalArgumentException();
		return size;
	}

	protected AbstractShape(Point center) {
		this.center.move(center.getX(), center.getY());
	}

	// figura con centro sull'origine degli assi

	protected AbstractShape() {
	}

	@Override
	public void move(double dx, double dy) {
		center.move(dx, dy);
	}

	@Override
	public Point getCenter() {
		return center;
	}

}
