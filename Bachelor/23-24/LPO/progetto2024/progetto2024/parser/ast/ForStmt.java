package progetto2024.parser.ast;

import static java.util.Objects.requireNonNull;
import progetto2024.visitors.Visitor;

public class ForStmt extends AbstractAssignStmt {
    private final Block block; // non-optional field

    public ForStmt(Variable var, Exp exp , Block block) {
		super(var, exp);
        this.block = requireNonNull(block);
	}

    @Override
    public String toString() {
        return String.format("%s(var %s of %s, %s)", getClass().getSimpleName(), var, exp, block);
    }

    @Override
    public <T> T accept(Visitor<T> visitor) {
        return visitor.visitForStmt(var, exp, block);
    }
}