package lab04;

public class Point {
	private double x;
	private double y;

	public Point() {
	}

	public Point(double x, double y) {
		this.x = x;
		this.y = y;
	}

	public Point(Point p) {
		this(p.x, p.y);
	}

	public double getX() {
		return this.x;
	}

	public double getY() {
		return this.y;
	}

	public void move(double dx, double dy) {
		this.x += dx;
		this.y += dy;
	}

	public boolean overlaps(Point p) {
		return this.x == p.x && this.y == p.y;
	}

}
