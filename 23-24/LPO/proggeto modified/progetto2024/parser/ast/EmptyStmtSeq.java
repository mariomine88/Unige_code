package progetto2024.parser.ast;

import progetto2024.visitors.Visitor;

public class EmptyStmtSeq extends EmptySeq<Stmt> implements StmtSeq {

	@Override
	public <T> T accept(Visitor<T> visitor) {
		return visitor.visitEmptyStmtSeq();
	}
}
