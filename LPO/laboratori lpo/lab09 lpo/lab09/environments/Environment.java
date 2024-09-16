package lab09.environments;

import lab09.parser.ast.NamedEntity;

public interface Environment<T> {

	/* adds a new nested scope */

	void enterScope();

	/* removes the most nested scope */

	void exitScope();

	/*
	 * looks up the value associated with 'var' starting from the innermost scope;
	 * throws an 'EnvironmentException' if 'var' could not be found in any scope
	 */

	T lookup(NamedEntity var);

	/*
	 * updates the innermost scope by associating 'var' with 'info'; 'var' is not allowed
	 * to be already defined, 'var' and 'info' must be non-null
	 */

	T dec(NamedEntity var, T info);

	/*
	 * updates the innermost scope which defines 'var' by associating 'var' with
	 * 'info'; throws an 'EnvironmentException' if 'var' could not be found in any
	 * scope; 'var' and 'info' must be non-null
	 */

	T update(NamedEntity var, T info);

}
