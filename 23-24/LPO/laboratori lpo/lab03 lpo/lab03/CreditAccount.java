package lab03;

/*
 *@ invariant: this.owner!=null && this.id>=0 && this.balance>=this.limit && \forall CreditAccount c1,c2; (acc1.id==acc2.id)==(acc1==acc2)
 */

public class CreditAccount {
	private static long nextId;
	private static final int defaultLimit = 100_00; // in cents

	private int limit; // in cents
	private int balance; // in cents
	private final Person owner;
	private final long id;

	// private auxiliary class methods for validation and identifier generation

	private static Person requireNonNull(Person p) {
		if (p == null)
			throw new NullPointerException();
		return p;
	}

	private static int requirePositive(int amount) {
		if (amount <= 0)
			throw new IllegalArgumentException();
		return amount;
	}

	private static int requireLimitBelowBalance(int limit, int balance) {
		if (limit > balance)
			throw new IllegalArgumentException();
		return limit;
	}

	private static long nextId() {
		if (CreditAccount.nextId < 0)
			throw new RuntimeException("No more available ids");
		return CreditAccount.nextId++;
	}

	// constructor

	private CreditAccount(int limit, int balance, Person owner) {
		this.balance = balance;
		this.limit = CreditAccount.requireLimitBelowBalance(limit, balance);
		this.owner = CreditAccount.requireNonNull(owner);
		this.id = CreditAccount.nextId();
	}

	// factory class methods

	public static CreditAccount newOfLimitBalanceOwner(int limit, int balance, Person owner) {
		return new CreditAccount(limit, balance, owner);
	}

	public static CreditAccount newOfBalanceOwner(int balance, Person owner) {
		return new CreditAccount(CreditAccount.defaultLimit, balance, owner);
	}

	// object methods

	public int deposit(int amount) { // amount in cents
		return this.balance = Math.addExact(this.balance, CreditAccount.requirePositive(amount)); // overflow is
																									// possible
	}

	public int withdraw(int amount) { // amount in cents
		int newBalance = Math.subtractExact(this.balance, CreditAccount.requirePositive(amount)); // balance can be
																									// negative,
																									// overflow is
																									// possible!
		CreditAccount.requireLimitBelowBalance(this.limit, newBalance);
		return this.balance = newBalance;
	}

	// getters

	public static int getDefaultLimit() {
		return CreditAccount.defaultLimit;
	}

	public int getBalance() {
		return this.balance;
	}

	public int getLimit() {
		return this.limit;
	}

	public Person getOwner() {
		return this.owner;
	}

	public long getId() {
		return this.id;
	}

	// setter
	
	public void setLimit(int limit) { // setter method
		this.limit = CreditAccount.requireLimitBelowBalance(limit, this.balance);
	}

}
