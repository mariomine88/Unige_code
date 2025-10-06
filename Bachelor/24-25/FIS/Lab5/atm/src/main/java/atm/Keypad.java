package atm;

import java.util.Scanner;

public class Keypad {

   private Scanner input; // reads data from the command line
                         
   public Keypad() {
      input = new Scanner(System.in);    
   }

   // Return an integer value entered by user, or -1 if input is invalid
   public int getInput() {
      String userInput = input.next(); // Read input as string
      try {
         return Integer.parseInt(userInput); // Try parsing as integer
      } catch (NumberFormatException e) {
         return -1; // Return -1 if not a valid integer
      }
   }

   // Return a double value entered by user, or -1 if input is invalid
   public double getDoubleInput() {
      String userInput = input.next(); // Read input as string
      try {
         return Double.parseDouble(userInput); // Try parsing as double
      } catch (NumberFormatException e) {
         return -1; // Return -1 if not a valid double
      }
   }
}
