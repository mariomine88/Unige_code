package lab09.visitors.typechecking;

import lab09.environments.EnvironmentException;
import lab09.parser.ast.Block;
import lab09.parser.ast.Exp;
import lab09.parser.ast.Stmt;
import lab09.parser.ast.StmtSeq;
import lab09.parser.ast.Variable;
import lab09.visitors.Visitor;
import static lab09.visitors.typechecking.AtomicType.*;

public class Typecheck implements Visitor<Type> {

	private final StaticEnv env = new StaticEnv();

    // useful to typecheck binary operations where operands must have the same type 
	private void checkBinOp(Exp left, Exp right, Type type) {
		type.checkEqual(left.accept(this));
		type.checkEqual(right.accept(this));
	}

	// static semantics for programs; no value returned by the visitor

	@Override
	public Type visitMyLangProg(StmtSeq stmtSeq) {
		try {
			stmtSeq.accept(this);
		} catch (EnvironmentException e) { // undeclared variable
			throw new TypecheckerException(e);
		}
		return null;
	}

	// static semantics for statements; no value returned by the visitor

	@Override
	public Type visitAssignStmt(Variable var, Exp exp) {
		var found = env.lookup(var);
		found.checkEqual(exp.accept(this));
		return null;
	}

	@Override
	public Type visitPrintStmt(Exp exp) {
		exp.accept(this);
		return null;
	}

	@Override
	public Type visitVarStmt(Variable var, Exp exp) {
		env.dec(var, exp.accept(this));
		return null;
	}

	@Override
	public Type visitIfStmt(Exp exp, Block thenBlock, Block elseBlock) {
		BOOL.checkEqual(exp.accept(this));
		thenBlock.accept(this);
		if (elseBlock != null) {
			elseBlock.accept(this);
		}
		return null;
	}

	@Override
	public Type visitBlock(StmtSeq stmtSeq) {
		env.enterScope();
		stmtSeq.accept(this);
		env.exitScope();
		return null;
	}

	// static semantics for sequences of statements
	// no value returned by the visitor

	@Override
	public Type visitEmptyStmtSeq() {
	    return null;
	}

	@Override
	public Type visitNonEmptyStmtSeq(Stmt first, StmtSeq rest) {
		first.accept(this);
		rest.accept(this);
		return null;
	}

	// static semantics of expressions; a type is returned by the visitor

	@Override
	public AtomicType visitAdd(Exp left, Exp right) {
		checkBinOp(left, right, INT);
		return INT;
	}

	@Override
	public AtomicType visitIntLiteral(int value) {
	    return INT;
	}

	@Override
	public AtomicType visitMul(Exp left, Exp right) {
	    checkBinOp(left, right, INT);
		return INT;
	}

	@Override
	public AtomicType visitSign(Exp exp) {
		INT.checkEqual(exp.accept(this));
		return INT;
	}

	@Override
	public Type visitVariable(Variable var) {
	    return env.lookup(var);
	}

	@Override
	public AtomicType visitNot(Exp exp) {
		BOOL.checkEqual(exp.accept(this));
		return BOOL;
	}

	@Override
	public AtomicType visitAnd(Exp left, Exp right) {
		checkBinOp(left, right, BOOL);
		return BOOL;
	}

	@Override
	public AtomicType visitBoolLiteral(boolean value) {
	    return BOOL;
	}

	@Override
	public AtomicType visitEq(Exp left, Exp right) {
		left.accept(this).checkEqual(right.accept(this));
		return BOOL;			
	}

	@Override
	public PairType visitPairLit(Exp left, Exp right) {
	    return new PairType(left.accept(this), right.accept(this));
	}

	@Override
	public Type visitFst(Exp exp) {
		return exp.accept(this).getFstPairType();
	}

	@Override
	public Type visitSnd(Exp exp) {
		return exp.accept(this).getSndPairType();
	}

}
