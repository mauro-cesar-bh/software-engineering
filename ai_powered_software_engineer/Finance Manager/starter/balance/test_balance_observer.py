import io
import unittest
from contextlib import redirect_stdout

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from balance.balance import Balance
from balance.balance_observer import (
    IBalanceObserver,
    LowBalanceAlertObserver,
    PrintBalance,
)


class TestLowBalanceAlertObserver(unittest.TestCase):
    """Tests that LowBalanceAlertObserver sets alert_triggered when the balance
    is below its threshold, and clears it when the balance recovers.
    """

    def setUp(self):
        """Get the shared Balance and reset it so every test starts at 0.0."""
        self.balance = Balance.get_instance()
        self.balance.reset()

    def _register(self, observer):
        """Register an observer; unregister it after the test."""
        self.balance.register_observer(observer)
        self.addCleanup(self.balance.unregister_observer, observer)
        return observer

    def test_alert_not_triggered_initially(self):
        """A new observer starts with alert_triggered set to False."""
        observer = LowBalanceAlertObserver(threshold=50)
        self.assertFalse(observer.alert_triggered)

    def test_alert_triggers_on_low_balance(self):
        """With threshold 50, the alert toggles as the balance crosses it.

        Sequence: 100 (off), 40 (on), 140 (off), 80 (off), 20 (on).
        """
        observer = self._register(LowBalanceAlertObserver(threshold=50))

        self.balance.apply_transaction(
            Transaction(100, TransactionCategory.INCOME)
        )
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE)
        )
        self.assertTrue(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(100, TransactionCategory.INCOME)
        )
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE)
        )
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE)
        )
        self.assertTrue(observer.alert_triggered)

    def test_no_alert_when_balance_equals_threshold(self):
        """A balance equal to the threshold (50) is not low."""
        observer = self._register(LowBalanceAlertObserver(threshold=50))

        self.balance.apply_transaction(
            Transaction(50, TransactionCategory.INCOME)
        )

        self.assertFalse(observer.alert_triggered)

    def test_alert_when_balance_just_below_threshold(self):
        """A balance of 49 with threshold 50 triggers the alert."""
        observer = self._register(LowBalanceAlertObserver(threshold=50))

        self.balance.apply_transaction(
            Transaction(49, TransactionCategory.INCOME)
        )

        self.assertTrue(observer.alert_triggered)

    def test_alert_triggers_when_balance_is_negative(self):
        """A balance of -10 with threshold 0 triggers the alert."""
        observer = self._register(LowBalanceAlertObserver(threshold=0))

        self.balance.apply_transaction(
            Transaction(10, TransactionCategory.EXPENSE)
        )

        self.assertTrue(observer.alert_triggered)

    def test_alert_message_is_printed_when_below_threshold(self):
        """Below the threshold, update() prints a 'Low balance alert'."""
        observer = LowBalanceAlertObserver(threshold=50)
        output = io.StringIO()

        with redirect_stdout(output):
            observer.update(40, Transaction(60, TransactionCategory.EXPENSE))

        self.assertIn("Low balance alert", output.getvalue())

    def test_no_message_is_printed_when_above_threshold(self):
        """At or above the threshold, update() prints nothing."""
        observer = LowBalanceAlertObserver(threshold=50)
        output = io.StringIO()

        with redirect_stdout(output):
            observer.update(100, Transaction(100, TransactionCategory.INCOME))

        self.assertEqual(output.getvalue(), "")

    def test_observer_with_different_thresholds_are_independent(self):
        """Thresholds 10 and 100 react separately to a balance of 50.

        The threshold-10 observer stays off; the threshold-100 one turns on.
        """
        low = self._register(LowBalanceAlertObserver(threshold=10))
        high = self._register(LowBalanceAlertObserver(threshold=100))

        self.balance.apply_transaction(
            Transaction(50, TransactionCategory.INCOME)
        )

        self.assertFalse(low.alert_triggered)
        self.assertTrue(high.alert_triggered)


class TestPrintBalance(unittest.TestCase):
    """Tests that PrintBalance prints each transaction and the new balance."""

    def setUp(self):
        """Get the shared Balance and reset it so every test starts at 0.0."""
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_update_prints_transaction_and_balance(self):
        """Calling update() prints the transaction and balance."""
        observer = PrintBalance()
        transaction = Transaction(100, TransactionCategory.INCOME)
        output = io.StringIO()

        with redirect_stdout(output):
            observer.update(100, transaction)

        self.assertIn(str(transaction), output.getvalue())
        self.assertIn("100", output.getvalue())

    def test_prints_on_every_balance_change(self):
        """Registered with Balance, PrintBalance prints one line per change.

        After +100 and -30, the second line shows the new balance, 70.
        """
        observer = PrintBalance()
        self.balance.register_observer(observer)
        self.addCleanup(self.balance.unregister_observer, observer)
        output = io.StringIO()

        with redirect_stdout(output):
            self.balance.apply_transaction(
                Transaction(100, TransactionCategory.INCOME)
            )
            self.balance.apply_transaction(
                Transaction(30, TransactionCategory.EXPENSE)
            )

        lines = output.getvalue().strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("70", lines[1])


class TestIBalanceObserver(unittest.TestCase):
    """Tests the abstract base class IBalanceObserver.

    IBalanceObserver is an interface with no real behavior. Every concrete
    observer (such as PrintBalance or LowBalanceAlertObserver) must override
    update(). These tests check that the base class refuses to run, so a
    subclass that forgets update() fails loudly instead of silently doing
    nothing.
    """

    def test_update_must_be_implemented_by_subclasses(self):
        """Calling update() on the base class raises NotImplementedError."""
        observer = IBalanceObserver()
        with self.assertRaises(NotImplementedError):
            observer.update(0, Transaction(1, TransactionCategory.INCOME))


if __name__ == "__main__":
    unittest.main()
