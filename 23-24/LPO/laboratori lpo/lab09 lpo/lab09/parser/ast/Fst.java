package lab09.parser.ast;

import lab09.visitors.Visitor;

public class Fst extends UnaryOp {

	public Fst(Exp exp) {
		super(exp);
	}
	
	@Override
	public <T> T accept(Visitor<T> visitor) {
		return visitor.visitFst(exp);
	}
}