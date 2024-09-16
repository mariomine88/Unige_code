package lab03;

public class TestCreditAccount {

	public static void main(String[] args) {
		Person guido = new Person("Guido", "Guerrieri");
		Person lorenza = new Person("Lorenza", "Delle Foglie");
		CreditAccount guidoAcc = CreditAccount.newOfBalanceOwner(100_00, guido);
		CreditAccount lorenzaAcc = CreditAccount.newOfLimitBalanceOwner(-500_00, 100_00, lorenza);
		assert guidoAcc.getId() == 0;
		assert guidoAcc.getOwner() == guido;
		assert guidoAcc.getBalance() == 100_00;
		assert guidoAcc.getLimit() == 100_00;
		assert lorenzaAcc.getId() == 1;
		assert lorenzaAcc.getOwner() == lorenza;
		assert lorenzaAcc.getBalance() == 100_00;
		assert lorenzaAcc.getLimit() == -500_00;
		assert guidoAcc.deposit(100_00) == 200_00;
		assert lorenzaAcc.deposit(200_00) == 300_00;
		assert guidoAcc.withdraw(50_00) == 150_00;
		lorenzaAcc.setLimit(100_00);
		assert lorenzaAcc.withdraw(200_00) == 100_00;
	}

}
