package lab03;

public class TestPerson {

	public static void main(String[] args) {
		Person guido = new Person("Guido", "Guerrieri");
		assert guido.getName().equals("Guido");
		assert guido.getSurname().equals("Guerrieri");
		assert guido.isSingle();
		Person lorenza = new Person("Lorenza", "Delle Foglie");
		assert lorenza.getName().equals("Lorenza");
		assert lorenza.getSurname().equals("Delle Foglie");
		assert lorenza.isSingle();
		Person.join(lorenza, guido);
		assert lorenza.getSpouse() == guido && guido.getSpouse() == lorenza;
		assert !lorenza.isSingle() && !guido.isSingle();
		Person.divorce(guido, lorenza);
		assert lorenza.isSingle();
		assert guido.isSingle();
	}

}
