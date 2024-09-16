package lab08.parser.ast;

public class DictUpdate extends TernaryOp {
    public DictUpdate(Exp first, Exp second, Exp third) {
        super(first, second, third);
    }
}