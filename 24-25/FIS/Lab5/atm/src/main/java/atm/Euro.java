package atm;

public class Euro {

	private double value;

	public Euro(double v) {
		value = v;
	}

	public double getValue() {
		return value;
	}

	public Euro sum(Euro e) {
		this.value = this.value + e.getValue();
		return this;
	}

	public Euro subtract(Euro e) {
		this.value = this.value - e.getValue();
		return this;
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