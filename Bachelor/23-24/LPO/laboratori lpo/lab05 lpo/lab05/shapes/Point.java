package lab05.shapes;

public interface Point {

	double getX();

	double getY();

	void move(double dx, double dy);

	boolean overlaps(Point p);

}