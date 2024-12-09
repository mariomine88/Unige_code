package atm;

public class BalanceInquiry extends Transaction {

   public BalanceInquiry(int userAccountNumber, Screen atmScreen, BankDatabase atmBankDatabase){
      super(userAccountNumber, atmScreen, atmBankDatabase);
   }

   // perform transaction
   public void execute(){
      BankDatabase bankDatabase = getBankDatabase();
      Screen screen = getScreen();
      // get the available balance for the account involved
      double availableBalance = bankDatabase.getAvailableBalance(getAccountNumber());
      // get the total balance for the account involved
      double totalBalance = bankDatabase.getTotalBalance(getAccountNumber());
      // display the balance information on the screen
      screen.displayMessageLine("\nBalance Information:");
      screen.displayMessage(" - Available balance: "); 
      screen.displayEuroAmount(availableBalance);
      screen.displayMessage("\n - Total balance:     ");
      screen.displayEuroAmount(totalBalance);
      screen.displayMessageLine("");
   } 
} 