package lab08.parser.ast;

import static java.util.Objects.requireNonNull;

public class Block implements Stmt {
	private final StmtSeq stmtSeq;

	public Block(StmtSeq stmtSeq) {
		this.stmtSeq = requireNonNull(stmtSeq);
	}

	@Override
	public String toString() {
		return String.format("%s(%s)", getClass().getSimpleName(), stmtSeq);
	}
}
