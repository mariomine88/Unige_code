package lab09.parser.ast;

import lab09.visitors.Visitor;

public class Add extends BinaryOp {
	public Add(Exp left, Exp right) {
		super(left, right);
	}
	
	@Override
	public <T> T accept(Visitor<T> visitor) {
		return visitor.visitAdd(left, right);
	}
}
