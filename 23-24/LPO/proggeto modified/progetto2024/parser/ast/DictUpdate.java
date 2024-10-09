package progetto2024.parser.ast;

import progetto2024.visitors.Visitor;

public class DictUpdate extends TernaryOp {
    public DictUpdate(Exp first, Exp second, Exp third) {
        super(first, second, third);
    }

    @Override
    public <T> T accept(Visitor<T> visitor) {
        return visitor.visitDictUpdate(first, second, third);
    }
}
