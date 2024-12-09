package atm;

public class Account 
{

   private int accountNumber; // account number
   private int pin; // PIN for authentication
   private Euro availableBalance; // funds available for withdrawal
   private Euro totalBalance; // funds available + pending deposits

   public Account(int theAccountNumber, int thePIN, Euro theAvailableBalance, Euro theTotalBalance) {
      accountNumber = theAccountNumber;
      pin = thePIN;
      availableBalance = theAvailableBalance;
      totalBalance = theTotalBalance;
   } 

   // determines whether a user-specified PIN matches PIN in Account
   public boolean validatePIN(int userPIN) {
      return (userPIN == pin);
   } 
   
   // returns available balance
   public Euro getAvailableBalance() {
      return availableBalance;
   } 

   // returns the total balance
   public Euro getTotalBalance() {
      return totalBalance;
   }

   // credits an amount to the account
   public void credit(Euro amount) {
      totalBalance.sum(amount);
   } 

   // debits an amount from the account
   public void debit(Euro amount) {
      availableBalance.subtract(amount);
      totalBalance.subtract(amount);
   } 

   // returns account number
   public int getAccountNumber() {
      return accountNumber;  
   }

} 