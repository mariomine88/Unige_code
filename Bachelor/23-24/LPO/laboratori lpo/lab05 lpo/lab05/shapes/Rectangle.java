package lab05.shapes;

/*
 * Implementa rettangoli con lati paralleli agli assi
 */
public class Rectangle extends AbstractShape {
	/* invariant width > 0 && height > 0 */
	private double width = Rectangle.defaultSize;
	private double height = Rectangle.defaultSize;

	private void setWidthHeight(double width, double height) {
		this.width = Rectangle.requirePositive(width);
		this.height = Rectangle.requirePositive(height);
	}

	protected Rectangle(double width, double height, Point center) {
		super(center);
		setWidthHeight(width,height);
	}

	// rettangolo con centro sull'origine degli assi

	protected Rectangle(double width, double height) {
	    setWidthHeight(width,height);
	}

	// rettangolo con centro sull'origine degli assi e dimensioni di default

	protected Rectangle() {
		setWidthHeight(width,height);
	}
	
	// factory methods

	public static Rectangle ofWidthHeightCenter(double width, double height, Point center) {
		return new Rectangle(width, height, center);
	}

	public static Rectangle ofWidthHeight(double width, double height) {
		return new Rectangle(width, height);
	}

	public static Rectangle ofDefaultSize() {
		return new Rectangle();
	}

	// object methods

	// attenzione, le dimensioni potrebbero diventare 0 se il fattore di scala è troppo piccolo

	@Override
	public void scale(double factor) { 
		requirePositive(factor);
		this.width *= factor;
		this.height *= factor;

	}

	@Override
	public double perimeter() {
		return (2 * (this.width + this.height));
	}

	@Override
	public double area() {
		return (this.width * this.height);
	}

}
