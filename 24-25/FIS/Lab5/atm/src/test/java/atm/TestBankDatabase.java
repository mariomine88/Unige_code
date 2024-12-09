package atm;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertFalse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class TestBankDatabase {

    private BankDatabase bankDatabase;
    private Euro amount;

    @BeforeEach
    public void setUp() {
        bankDatabase = new BankDatabase();
        amount = new Euro(100.0);
    }

    @Test
    void testAuthenticateUser() {
        assertAll(
            () -> assertTrue(bankDatabase.authenticateUser(12345, 54321)),
            () -> assertFalse(bankDatabase.authenticateUser(12345, 12345)),
            () -> assertFalse(bankDatabase.authenticateUser(0, 54320))
        );
    }

    @Test
    void testGetAvailableBalance() {
        assertEquals(1000.0, bankDatabase.getAvailableBalance(12345).getValue());
    }

    @Test
    void testGetTotalBalance() {
        assertEquals(1200.0, bankDatabase.getTotalBalance(12345).getValue());
    }

    @Test
    void testCredit() {
        bankDatabase.credit(12345, amount);
        assertEquals(1300.0, bankDatabase.getTotalBalance(12345).getValue());
    }

    @Test
    void testDebit() {
        bankDatabase.debit(12345, amount);
        assertAll(
            () -> assertEquals(900.0, bankDatabase.getAvailableBalance(12345).getValue()),
            () -> assertEquals(1100.0, bankDatabase.getTotalBalance(12345).getValue())
        );
    }
}