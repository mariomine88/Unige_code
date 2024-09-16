package lab09.visitors;

import lab09.parser.ast.Block;
import lab09.parser.ast.Exp;
import lab09.parser.ast.Stmt;
import lab09.parser.ast.StmtSeq;
import lab09.parser.ast.Variable;

public interface Visitor<T> {
	T visitAdd(Exp left, Exp right);

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

	T visitBlock(StmtSeq stmtSeq);

	T visitPairLit(Exp left, Exp right);

	T visitFst(Exp exp);

	T visitSnd(Exp exp);
}
