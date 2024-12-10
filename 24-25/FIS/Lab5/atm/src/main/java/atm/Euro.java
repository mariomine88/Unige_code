package atm;

public class Euro {
	private double value;

	public Euro(double v) {
		value = v;
	}

	public double getValue() {
		return value;
	}

	public void sum(Euro e) {
		value += e.getValue();
	}

	public void subtract(Euro e) {
		value -= e.getValue();
	}

	public boolean equalTo(Euro e){
		return (value == e.getValue());
	}
	
	public boolean lessThan(Euro e){
		return (value <= e.getValue());
	}

	public String print(){
		return value +" euro";
	}
}