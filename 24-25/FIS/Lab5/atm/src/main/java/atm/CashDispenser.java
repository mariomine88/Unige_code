package atm;

public class CashDispenser 
{

   // the default initial number of bills in the cash dispenser
   private static final int INITIAL_COUNT = 500;
   private int count; // number of 20 Euro bills remaining
   
   public CashDispenser() {
      count = INITIAL_COUNT; // set count attribute to default
   }

   // simulates dispensing of specified amount of cash
   public void dispenseCash(double amount) {
      int billsRequired = (int) amount / 20; // number of 20 Euro bills required
      count -= billsRequired; // update the count of bills
   }

   // indicates whether cash dispenser can dispense desired amount
   public boolean isSufficientCashAvailable(double amount) {
      int billsRequired = (int) amount / 20; // number of 20 Euro bills required
      return (count >= billsRequired); 
   } 

}