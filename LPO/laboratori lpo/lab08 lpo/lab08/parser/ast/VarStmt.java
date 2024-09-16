package lab08.parser.ast;

public class VarStmt extends AbstractAssignStmt {

	public VarStmt(Variable var, Exp exp) {
		super(var, exp);
	}
}
