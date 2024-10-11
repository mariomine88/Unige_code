package progetto2024.visitors.execution;

import java.io.PrintWriter;
import static java.util.Objects.requireNonNull;
import progetto2024.environments.EnvironmentException;
import progetto2024.parser.ast.Block;
import progetto2024.parser.ast.Exp;
import progetto2024.parser.ast.Stmt;
import progetto2024.parser.ast.StmtSeq;
import progetto2024.parser.ast.Variable;
import progetto2024.visitors.Visitor;

public class Execute implements Visitor<Value> {

	private final DynamicEnv env = new DynamicEnv();
	private final PrintWriter printWriter; // output stream used to print values

	public Execute() {
		printWriter = new PrintWriter(System.out, true);
	}

	public Execute(PrintWriter printWriter) {
		this.printWriter = requireNonNull(printWriter);
	}

	// dynamic semantics for programs; no value returned by the visitor

	@Override
	public Value visitMyLangProg(StmtSeq stmtSeq) {
		try {
			stmtSeq.accept(this);
			// possible runtime errors
			// EnvironmentException: undefined variable
		} catch (EnvironmentException e) {
			throw new InterpreterException(e);
		}
		return null;
	}

	// dynamic semantics for statements; no value returned by the visitor

	@Override
	public Value visitAssignStmt(Variable var, Exp exp) {
		env.update(var, exp.accept(this));
		return null;
	}

	@Override
	public Value visitPrintStmt(Exp exp) {
		printWriter.println(exp.accept(this));
		return null;
	}

	@Override
	public Value visitVarStmt(Variable var, Exp exp) {
		env.dec(var, exp.accept(this));
		return null;
	}

	@Override
	public Value visitIfStmt(Exp exp, Block thenBlock, Block elseBlock) {
		if (exp.accept(this).toBool()) {
			thenBlock.accept(this);
		} else if (elseBlock != null) {
			elseBlock.accept(this);
		}
		return null;
	}

	@Override
	public Value visitForStmt(Variable var, Exp dict, Block block) {
		dict.accept(this).toDict().getDict().forEach((key, value) -> {
			env.enterScope();
			env.dec(var, new PairValue(new IntValue(key), value));
			block.accept(this);
			env.exitScope();
		});
		return null;
	}

	@Override
	public Value visitBlock(StmtSeq stmtSeq) {
		env.enterScope();
		stmtSeq.accept(this);
		env.exitScope();
		return null;
	}

	// dynamic semantics for sequences of statements
	// no value returned by the visitor

	@Override
	public Value visitEmptyStmtSeq() {
	    return null;
	}

	@Override
	public Value visitNonEmptyStmtSeq(Stmt first, StmtSeq rest) {
		first.accept(this);
		rest.accept(this);
		return null;
	}

	// dynamic semantics of expressions; a value is returned by the visitor

	@Override
	public IntValue visitAdd(Exp left, Exp right) {
		return new IntValue(left.accept(this).toInt() + right.accept(this).toInt());
	}

	@Override
	public IntValue visitIntLiteral(int value) {
	    return new IntValue(value);
	}

    	@Override
	public IntValue visitMul(Exp left, Exp right) {
	    return new IntValue(left.accept(this).toInt() * right.accept(this).toInt());
	}
    
	@Override
	public IntValue visitSign(Exp exp) {
		return new IntValue(-exp.accept(this).toInt());		
	}

	@Override
	public Value visitVariable(Variable var) {
	    return env.lookup(var);
	}

	@Override
	public BoolValue visitNot(Exp exp) {
		return new BoolValue(!exp.accept(this).toBool());
	}

	@Override
	public BoolValue visitAnd(Exp left, Exp right) {
	    return new BoolValue(left.accept(this).toBool() && right.accept(this).toBool());
	}

	@Override
	public BoolValue visitBoolLiteral(boolean value) {
	    return new BoolValue(value);
	}

	@Override
	public BoolValue visitEq(Exp left, Exp right) {
	    return new BoolValue(left.accept(this).equals(right.accept(this)));
	}

	@Override
	public PairValue visitPairLit(Exp left, Exp right) {
	    return new PairValue(left.accept(this), right.accept(this));
	}

	@Override
	public Value visitFst(Exp exp) {
		return exp.accept(this).toPair().getFstVal();
	}

	@Override
	public Value visitSnd(Exp exp) {
		return exp.accept(this).toPair().getSndVal();
	}

	@Override
	public DictValue visitDictLiteral(Exp key, Exp value) {
		return new DictValue(key.accept(this).toInt(), value.accept(this));
	}

	@Override
	public Value visitDictGet(Exp dict, Exp key) {
		return dict.accept(this).toDict().get(key.accept(this).toInt()); 
	}

	@Override
	public DictValue visitDictDel(Exp dict, Exp key){
		return new DictValue(dict.accept(this).toDict().remove(key.accept(this).toInt()));
	}

	@Override
	public DictValue visitDictUpdate(Exp dict, Exp key, Exp value){
		return new DictValue(dict.accept(this).toDict().put(key.accept(this).toInt(),value.accept(this)));
	}

}

