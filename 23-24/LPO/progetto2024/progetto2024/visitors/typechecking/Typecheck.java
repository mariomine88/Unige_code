package progetto2024.visitors.typechecking;

import progetto2024.environments.EnvironmentException;
import progetto2024.parser.ast.Block;
import progetto2024.parser.ast.Exp;
import progetto2024.parser.ast.Stmt;
import progetto2024.parser.ast.StmtSeq;
import progetto2024.parser.ast.Variable;
import progetto2024.visitors.Visitor;
import static progetto2024.visitors.typechecking.AtomicType.*;

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
	public Type visitForStmt(Variable var, Exp dict, Block block) {
		env.dec(var, new PairType( INT, dict.accept(this).getValueDictType()));
		block.accept(this);
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

	@Override
	public DictType visitDictLiteral(Exp key, Exp exp) {
		INT.checkEqual(key.accept(this));
		return new DictType(exp.accept(this));
	}

	
	@Override
	public Type visitDictGet(Exp dict, Exp key) {
		INT.checkEqual(key.accept(this));
		return dict.accept(this).getValueDictType();
	}

	@Override
	public DictType visitDictDel(Exp dict, Exp key) {
		INT.checkEqual(key.accept(this));
		return new DictType(dict.accept(this).getValueDictType());
	}
	
	@Override
	public DictType visitDictUpdate(Exp dict, Exp key, Exp exp) {
		INT.checkEqual(key.accept(this));
		dict.accept(this).getValueDictType().checkEqual(exp.accept(this));
		return new DictType(dict.accept(this).getValueDictType());
	}
}
