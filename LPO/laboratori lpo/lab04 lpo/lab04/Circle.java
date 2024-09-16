package lab04;

public class Circle implements Shape {
	// @ invariant: radius > 0

	private static final double defaultSize = 1;
	private double radius = Circle.defaultSize;
	private final Point center = new Point();

	private static double requirePositive(double size) {
		if (size <= 0) {
			throw new IllegalArgumentException("size must be positive");
		}
		return size;
	}

	private Circle(double radius, Point center) {
		if (requirePositive(radius) == radius) {
			this.radius = radius;
		}
		this.center.move(center.getX(), center.getY());
	}

	// cerchio con centro sull'origine degli assi

	private Circle(double radius) {
		if (requirePositive(radius) == radius) {
			this.radius = radius;
		}
	}

	// cerchio con dimensioni di default e centro sull'origine degli assi

	public Circle() {
		this.radius = defaultSize;
	}

	// metodi di classe factory

	public static Circle ofRadius(double radius) {
		return new Circle(radius);
	}

	public static Circle ofRadiusCenter(double radius, Point center) {
		return new Circle(radius, center);
	}

	// metodi di oggetto

	public void move(double dx, double dy) {
		this.center.move(dx, dy);
	}

	// attenzione, il raggio potrebbe diventare 0 se il fattore di scala è troppo piccolo

	public void scale(double factor) {
		if (factor <= 0) {
			throw new IllegalArgumentException("factor must be positive");
		}
		this.radius *= factor;
	}

	// restituisce copia per garantire onwership esclusiva

	public Point getCenter() {
		return new Point(this.center.getX(), this.center.getY());
	}

	public double perimeter() {
		double pigreco = 3.14159; // approximate value of pigreco
		return 2*(pigreco * this.radius);
	}

	public double area() {
		double pigreco = 3.14159; // approximate value of pigreco
		return pigreco*(this.radius * this.radius); // area = pigreco * r^2
	}

}
