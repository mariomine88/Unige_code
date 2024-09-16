package lab05.shapes;

public class Circle extends AbstractShape {
	/* invariant radius > 0 */
	private double radius = Circle.defaultSize;

	// private object method to be used in the constructors
	private void setRadius(double radius) {
		this.radius = Circle.requirePositive(radius);
	}

	protected Circle(double radius, Point center) {
		super(center);
		setRadius(radius);
	}

	// cerchio con centro sull'origine degli assi

	protected Circle(double radius) {
	    setRadius(radius);
	}

	// cerchio con centro sull'origine degli assi e raggio di default

	protected Circle() {
		setRadius(radius);
	}
	
	// factory methods

	public static Circle ofRadiusCenter(double radius, Point center) {
		return new Circle(radius, center);
	}

	public static Circle ofRadius(double radius) {
		return new Circle(radius);
	}

	public static Circle ofDefaultSize() {
		return new Circle();
	}

	// object methods

	// attenzione, il raggio potrebbe diventare 0 se il fattore di scala è troppo piccolo

	@Override
	public void scale(double factor) {
		requirePositive(factor);
		this.radius *= factor;
	}

	@Override
	public double perimeter() {
	    return 2*(Math.PI * this.radius);
	}

	@Override
	public double area() {
	    return Math.PI * Math.pow(this.radius, 2);
	}

}
