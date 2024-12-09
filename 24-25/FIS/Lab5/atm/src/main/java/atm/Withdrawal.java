package atm;

public class Withdrawal extends Transaction {

   private Keypad keypad;
   private CashDispenser cashDispenser;
   private static final int CANCELED = 0;
   private static final int INVALID = 6;

   public Withdrawal(int userAccountNumber, Screen atmScreen, BankDatabase atmBankDatabase, 
                     Keypad atmKeypad, CashDispenser atmCashDispenser) {
      super( userAccountNumber, atmScreen, atmBankDatabase );
      keypad = atmKeypad;
      cashDispenser = atmCashDispenser;
   }

   // perform transaction
   public void execute() {
      boolean cashDispensed = false; // cash was not dispensed yet
      double availableBalance; // amount available for withdrawal
      // get references to bank database and screen
      BankDatabase bankDatabase = getBankDatabase(); 
      Screen screen = getScreen();
      // loop until cash is dispensed or the user cancels
      do {
         // obtain a chosen withdrawal amount from the user 
         double amount = displayMenuOfAmounts();
         // check whether user chose a withdrawal amount or canceled
         if (amount != CANCELED) {
            // get available balance of account involved
            availableBalance = bankDatabase.getAvailableBalance(getAccountNumber());
            // check whether the user has enough money in the account 
            if (amount <= availableBalance) {   
               // check whether the cash dispenser has enough money
               if (cashDispenser.isSufficientCashAvailable(amount)) {
                  // update the account involved to reflect withdrawal
                  bankDatabase.debit(getAccountNumber(), amount);
                  cashDispenser.dispenseCash(amount); // dispense cash
                  cashDispensed = true; // cash was dispensed
                  // instruct user to take cash
                  screen.displayMessageLine("\nPlease take your cash now.");
               } 
               else // cash dispenser does not have enough cash
                  screen.displayMessageLine("""
                     Insufficient cash available in the ATM.
                     Please choose a smaller amount.
                  """);
            } 
            else // not enough money available in user's account
               screen.displayMessageLine("""
                  Insufficient funds in your account.
                  Please choose a smaller amount.
               """);
         } 
         else { // user chose cancel menu option 
            screen.displayMessageLine("\nCanceling transaction...");
            break;
         }
      } while (!cashDispensed);
   }

   // display a menu of withdrawal amounts and the option to cancel
   // return the chosen amount or 0 if the user chooses to cancel
   private int displayMenuOfAmounts()
   {
      int userChoice = 6; // local variable to store return value
      Screen screen = getScreen();
      // array of amounts to correspond to menu numbers
      int [] amounts = { 0, 20, 40, 60, 100, 200 };
      // loop while no valid choice has been made
      while (userChoice == INVALID) {
         // display the menu
         screen.displayMessageLine("\nWithdrawal Menu:");
         screen.displayMessageLine("1 - 20 Euro");
         screen.displayMessageLine("2 - 40 Euro");
         screen.displayMessageLine("3 - 60 Euro");
         screen.displayMessageLine("4 - 100 Euro");
         screen.displayMessageLine("5 - 200 Euro");
         screen.displayMessageLine("0 - Cancel transaction");
         screen.displayMessage("\nChoose a withdrawal amount: ");
         int input = keypad.getInput(); // get user input through keypad
         // determine how to proceed based on the input value
         switch (input) {
             // if the user chose a withdrawal amount (i.e., chose option 1, 2, 3, 4 or 5)
             // return the corresponding amount from amounts array
            case 1, 2, 3, 4, 5:
               userChoice = amounts[input]; // save user's choice
               break;       
            case CANCELED: // the user chose to cancel
               userChoice = CANCELED; // save user's choice
               break;
            default: // the user did not enter a valid value
               screen.displayMessageLine("\nIvalid selection. Try again.");
         }
      } 
      return userChoice; // return withdrawal amount or CANCELED
   }
}