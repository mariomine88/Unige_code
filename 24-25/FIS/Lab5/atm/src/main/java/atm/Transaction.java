package atm;

public abstract class Transaction
{

   private int accountNumber; // indicates account involved
   private Screen screen; // ATM's screen
   private BankDatabase bankDatabase; // account info database

   Transaction(int userAccountNumber, Screen atmScreen, BankDatabase atmBankDatabase){
      accountNumber = userAccountNumber;
      screen = atmScreen;
      bankDatabase = atmBankDatabase;
   } 

   public int getAccountNumber(){
      return accountNumber; 
   }

   public Screen getScreen(){
      return screen;
   }

   public BankDatabase getBankDatabase(){
      return bankDatabase;
   }
   
   // perform the transaction (overridden by each subclass)
   public abstract void execute();
   
}