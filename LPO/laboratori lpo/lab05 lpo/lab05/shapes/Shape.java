package lab05.shapes;

public interface Shape {
	// restituisce una copia del centro della figura

	Point getCenter();

	// restituisce il perimetro della figura

	double perimeter();

	// restituisce l'area della figura

	double area();

	// trasla la figura lungo il vettore (dx,dy)

	void move(double dx, double dy);

	// scala la figura del fattore di scala factor, senza muovere il centro

	// @ requires: factor > 0

	void scale(double factor);

}
