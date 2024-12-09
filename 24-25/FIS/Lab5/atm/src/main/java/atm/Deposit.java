package atm;

public class Deposit extends Transaction {

   private Keypad keypad;
   private DepositSlot depositSlot;
   private static final int CANCELED = 0; // constant for cancel option

   public Deposit(int userAccountNumber, Screen atmScreen, BankDatabase atmBankDatabase, Keypad atmKeypad, 
                  DepositSlot atmDepositSlot){
      super(userAccountNumber, atmScreen, atmBankDatabase);
      keypad = atmKeypad;
      depositSlot = atmDepositSlot;
   }

   // perform transaction
   public void execute(){
      BankDatabase bankDatabase = getBankDatabase();
      Screen screen = getScreen();
      double amount = -1;
      do{
         amount = promptForDepositAmount(); // get deposit amount from user
      }
      while(amount <0);
      // check whether user entered a deposit amount or canceled
      if (amount != CANCELED) {
         // request deposit envelope containing specified amount
         screen.displayMessage("\nPlease insert a deposit envelope containing ");
         screen.displayEuroAmount(amount);
         screen.displayMessageLine(".");
         // receive deposit envelope
         boolean envelopeReceived = depositSlot.isEnvelopeReceived();
         // check whether deposit envelope was received
         if (envelopeReceived) {  
            String msg = """
               Your envelope has been received.
               NOTE: The money just deposited will not be available until we verify the amount of any enclosed cash and your checks clear.
               """;
            screen.displayMessageLine(msg);
            // credit account to reflect the deposit
            bankDatabase.credit(getAccountNumber(), amount); 
         }
         else // deposit envelope not received
            screen.displayMessageLine( "\nYou did not insert an " +
               "envelope, so the ATM has canceled your transaction.");
      }
      else // user canceled instead of entering amount
         screen.displayMessageLine("\nCanceling transaction...");
   }

   // prompt user to enter a deposit amount in cents 
   private double promptForDepositAmount() {
      Screen screen = getScreen();
      // display the prompt
      screen.displayMessage("\nPlease enter a valid deposit amount or 0 to cancel: ");
      double input = keypad.getDoubleInput(); // receive input of deposit amount
      // check whether the user canceled or entered a valid amount
      if (input == 0) 
         return CANCELED;
      else
         return input; // return euro amount 
   } 
   
}