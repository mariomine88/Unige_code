package progetto2024.parser.ast;

import progetto2024.visitors.Visitor;

public class AssignStmt extends AbstractAssignStmt {

	public AssignStmt(Variable var, Exp exp) {
		super(var, exp);
	}
	
	@Override
	public <T> T accept(Visitor<T> visitor) {
		return visitor.visitAssignStmt(var, exp);
	}
}
