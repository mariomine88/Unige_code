package progetto2024.visitors;

import progetto2024.parser.ast.Block;
import progetto2024.parser.ast.Exp;
import progetto2024.parser.ast.Stmt;
import progetto2024.parser.ast.StmtSeq;
import progetto2024.parser.ast.Variable;

public interface Visitor<T> {
	T visitAdd(Exp left, Exp right);

	T visitDiv(Exp left, Exp right);

	T visitAssignStmt(Variable var, Exp exp);

	T visitIntLiteral(int value);

	T visitEq(Exp left, Exp right);

	T visitNonEmptyStmtSeq(Stmt first, StmtSeq rest);

	T visitMul(Exp left, Exp right);

	T visitPrintStmt(Exp exp);

	T visitMyLangProg(StmtSeq stmtSeq);

	T visitSign(Exp exp);

	T visitVariable(Variable var); // only in this case more efficient then T visitVariable(String name)

	T visitEmptyStmtSeq();

	T visitVarStmt(Variable var, Exp exp);

	T visitNot(Exp exp);

	T visitAnd(Exp left, Exp right);

	T visitBoolLiteral(boolean value);

	T visitIfStmt(Exp exp, Block thenBlock, Block elseBlock);

	T visitForStmt(Variable var, Exp dict, Block block);

	T visitBlock(StmtSeq stmtSeq);

	T visitPairLit(Exp left, Exp right);

	T visitFst(Exp exp);

	T visitSnd(Exp exp);

	T visitDictLiteral(Exp left, Exp right);
	
	T visitDictGet(Exp left, Exp right);

	T visitDictDel(Exp left, Exp right);

	T visitDictUpdate(Exp first, Exp second, Exp third);
}
