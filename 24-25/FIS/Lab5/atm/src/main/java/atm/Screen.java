package atm;

public class Screen
{

   // displays a message without a carriage return
   public void displayMessage(String message) {
      System.out.print(message); 
   } 

   // display a message with a carriage return
   public void displayMessageLine (String message) {
      System.out.println(message);   
   }

   // display a euro amount
   public void displayEuroAmount(double amount) {
      System.out.printf("Euro %,.2f", amount);   
   }
   
}