package progetto2024.parser.ast;

import progetto2024.visitors.Visitor;

public class Div extends BinaryOp {
	public Div(Exp left, Exp right) {
		super(left, right);
	}

	@Override
	public <T> T accept(Visitor<T> visitor) {
		return visitor.visitDiv(left, right);
	}
}
