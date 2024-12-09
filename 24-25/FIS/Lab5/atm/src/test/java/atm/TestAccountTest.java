package atm;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class TestAccountTest {

    private Account account;
    private Euro availableBalance;
    private Euro totalBalance;

    @BeforeEach
    public void setUp() {
        availableBalance = new Euro(1000);
        totalBalance = new Euro(1500);
        account = new Account(12345, 6789, availableBalance, totalBalance);
    }

    @Test
    void testValidatePIN() {
        assertTrue(account.validatePIN(6789));
    }

    @Test
    void testGetAvailableBalance() {
        assertEquals(availableBalance, account.getAvailableBalance());
    }

    @Test
    void testGetTotalBalance() {
        assertEquals(totalBalance, account.getTotalBalance());
    }

    @Test
    void testCredit() {
        Euro amount = new Euro(500);
        account.credit(amount);
        assertTrue(account.getTotalBalance().equalTo(new Euro(2000)));
    }

    @Test
    void testDebit() {
        Euro amount = new Euro(200);
        account.debit(amount);
        assertAll(
            () -> assertTrue(account.getAvailableBalance().equalTo(new Euro(800))),
            () -> assertTrue(account.getTotalBalance().equalTo(new Euro(1300)))
        );
    }

    @Test
    void testGetAccountNumber() {
        assertEquals(12345, account.getAccountNumber());
    }
}