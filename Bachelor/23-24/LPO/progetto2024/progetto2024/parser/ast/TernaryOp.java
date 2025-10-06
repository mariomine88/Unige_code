package progetto2024.parser.ast;

import static java.util.Objects.requireNonNull;

public abstract class TernaryOp implements Exp {
    protected final Exp first;
    protected final Exp second;
    protected final Exp third;

    protected TernaryOp(Exp first, Exp second, Exp third) {
        this.first = requireNonNull(first);
        this.second = requireNonNull(second);
        this.third = requireNonNull(third);
    }

    @Override
    public String toString() {
        return String.format("%s(%s,%s,%s)", getClass().getSimpleName(), first, second, third);
    }
}