package atm;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;


class TestEuro {
    private Euro euro1;
    private Euro euro2;

    @BeforeEach
    public void setUp() {
        euro1 = new Euro(530.5);
        euro2 = new Euro(100);
    }

    @Test
    void testSum() {
        euro1.sum(euro2);
        assertEquals(630.5, euro1.getValue());
    }

    @Test
    void testSubtract() {
        euro1.subtract(euro2);
        assertEquals(430.5, euro1.getValue());
    }

    @Test
    void testEqualTo() {
        Euro euro3 = new Euro(100);
        assertAll(
            () -> assertFalse(euro1.equalTo(euro3)),
            () -> assertTrue(euro2.equalTo(euro3))
        );
    }

    @Test
    void testLessThan() {
        assertAll(
            () -> assertTrue(euro2.lessThan(euro1)),
            () -> assertFalse(euro1.lessThan(euro2))
        );
    }

    @Test
    void testPrint() {
        assertEquals("530.5 euro", euro1.print());
    }
}