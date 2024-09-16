package lab08.parser.ast;

import static java.util.Objects.requireNonNull;

public class ForStmt implements Stmt {
    private final String ident; // non-optional field
    private final Exp exp; // non-optional field
    private final Block block; // non-optional field

    public ForStmt(String ident, Exp exp, Block block) {
        this.ident = requireNonNull(ident);
        this.exp = requireNonNull(exp);
        this.block = requireNonNull(block);
    }

    @Override
    public String toString() {
        return String.format("%s(var %s of %s, %s)", getClass().getSimpleName(), ident, exp, block);
    }
}