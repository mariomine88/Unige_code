package lab05.accounts;

public class AccountTest {

	public static void main(String[] args) {
		Client lorenza = new Person("Lorenza", "Delle Foglie");
		HistoryAccount lorenzaAccount = HistoryCreditAccount.newOfLimitBalance(-1000_00, 1000_00, lorenza);
		assert lorenzaAccount.withdraw(1000_00) == 0_00;
		assert lorenzaAccount.redo() == -1000_00;
		assert lorenzaAccount.undo() == 0_00;
		assert lorenzaAccount.deposit(2000_00) == 2000_00;
		assert lorenzaAccount.redo() == 4000_00;
		assert lorenzaAccount.redo() == 6000_00;
		assert lorenzaAccount.undo() == 4000_00;
		assert lorenzaAccount.getBalance() == 4000_00;
		assert lorenzaAccount.getLimit() == -1000_00;
	}

}
