package lab05.shapes;

/*
 * 2D Points implemented with Cartesian coordinates 
 */
public class PointClass implements Point {
	private double x;
	private double y;

	public PointClass() {
	}

	public PointClass(double x, double y) {
		this.x = x;
		this.y = y;
	}

	public PointClass(Point p) {
		this(p.getX(), p.getY());
	}

	@Override
	public double getX() {
		return x;
	}

	@Override
	public double getY() {
		return y;
	}

	@Override
	public void move(double dx, double dy) {
		x += dx;
		y += dy;
	}

	@Override
	public boolean overlaps(Point p) {
		return x == p.getX() && y == p.getY();
	}

}
