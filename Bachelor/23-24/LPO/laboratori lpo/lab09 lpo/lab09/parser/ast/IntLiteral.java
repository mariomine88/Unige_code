package lab09.parser.ast;

import lab09.visitors.Visitor;

public class IntLiteral extends AtomicLiteral<Integer> {

	public IntLiteral(int n) {
		super(n);
	}
	
	@Override
	public <T> T accept(Visitor<T> visitor) {
		return visitor.visitIntLiteral(value);
	}
}
