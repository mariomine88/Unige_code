package progetto2024.environments;

import static java.util.Objects.requireNonNull;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;

import progetto2024.parser.ast.NamedEntity;

public class GenEnvironment<T> implements Environment<T> {

	private LinkedList<HashMap<NamedEntity, T>> scopeChain = new LinkedList<>();

	/*
	 * enter a new nested scope; private method shared by 'enterScope()' and the
	 * constructor 'GenEnvironment()'
	 */
	private void addEmptyScope() {
		scopeChain.addFirst(new HashMap<>());
	}

	/* create an environment with just one empty scope */
	public GenEnvironment() {
		addEmptyScope();
	}

	@Override
	public void enterScope() {
		addEmptyScope();
	}

	@Override
	public void exitScope() {
		scopeChain.removeFirst();
	}

	/*
	 * looks up the innermost scope where 'var' is found;
	 * throws an 'EnvironmentException' if 'var' could not be found in any scope
	 */

	protected Map<NamedEntity, T> resolve(NamedEntity var) {
		for (var scope : scopeChain)
			if (scope.containsKey(var))
				return scope;
		throw new EnvironmentException("Undeclared " + var);
	}

	@Override
	public T lookup(NamedEntity var) {
		return resolve(var).get(var);
	}

	/*
	 * updates map to associate 'var' with 'info'; 'var' and 'info' must be non-null
	 */

	private static <T> T updateScope(Map<NamedEntity, T> map, NamedEntity var, T info) {
		return map.put(requireNonNull(var), requireNonNull(info));
	}

	/*
	 * updates the innermost scope by associating 'var' with 'info'; 'var' is not allowed
	 * to be already defined, 'var' and 'info' must be non-null
	 */

	@Override
	public T dec(NamedEntity var, T info) {
		var scope = scopeChain.getFirst();
		if (scope.containsKey(var))
			throw new EnvironmentException(var + " already declared");
		return updateScope(scope, var, info);
	}

	/*
	 * updates the 'info' of the innermost variable 'var', throws an 'EnvironmentException' if no varibale 'var' can be
	 * found in the scope chain. Only used for the dynamic semantics
	 */

	@Override
	public T update(NamedEntity var, T info) {
		var scope = resolve(var);
		return updateScope(scope, var, info);
	}

}
