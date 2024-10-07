package lab04;

// implementa rettangoli con lati paralleli agli assi
//rectangle è un sottotipo di shape
public class Rectangle implements Shape {
	//@ invariant: width > 0 && height > 0 
	
	public static final double defaultSize = 1;
	private double width = Rectangle.defaultSize;
	private double height = Rectangle.defaultSize;

	private final Point center = new Point(); 

	private static double requirePositive(double size) {
		//controllo che la size sia positiva e se non lo è lancio un eccezione
		if (size <= 0) {
			throw new IllegalArgumentException("size must be positive");
		}
		return size;
	}

	//metodi costruttori di classe

	private Rectangle(double width, double height, Point center) {
		if (requirePositive(width) == width && requirePositive(height) == height) {
			this.width = width;
			this.height = height;
		}
		this.center.move(center.getX(), center.getY());
		//sposto il centro del rettangolo perchènon posso assegnare ad una variabile final 			
	}

	// rettangolo con centro sull'origine degli assi

	private Rectangle(double width, double height) {
		if (requirePositive(width) == width && requirePositive(height) == height) {
			this.width = width;
			this.height = height;
		}
	}

	// rettangolo con dimensioni di default e centro sull'origine degli assi

	public Rectangle() {
		this.width = defaultSize;
		this.height = defaultSize;
	}

	// metodi di classe factory (richiamano il costruttore)

	public static Rectangle ofWidthHeight(double width, double height) {
		return new Rectangle(width, height);
	}

	public static Rectangle ofWidthHeightCenter(double width, double height, Point center) {
		return new Rectangle(width, height, center);
	}

	// metodi di oggetto

	public void move(double dx, double dy) {
		this.center.move(dx, dy);
	}

	// attenzione, le dimensioni potrebbero diventare 0 se il fattore di scala è
	// troppo piccolo

	public void scale(double factor) {
		if (factor > 0) {
			this.width *= factor;
			this.height *= factor;
		}
	}

	// restituisce copia per garantire onwership esclusiva

	public Point getCenter() {
		return new Point(this.center);	//ritorno una copia del centro
	}

	public double perimeter() {
		return (2 * (this.width + this.height)); //perimetro del rettangolo
	}

	public double area() {
		return (this.width * this.height); //area del rettangolo
	}

}
