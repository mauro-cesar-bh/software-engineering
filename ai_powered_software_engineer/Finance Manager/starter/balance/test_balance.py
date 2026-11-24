import unittest
from balance.balance import Balance
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class RecordingObserver:
    """Test double: an observer that stores every update it receives.

    Tests read `calls`, a list of (balance, transaction) pairs, to check
    exactly what Balance sent to it and how many times.
    """

    def __init__(self):
        self.calls = []

    def update(self, balance, transaction):
        """Record the balance and transaction that Balance passed in."""
        self.calls.append((balance, transaction))


class TestBalance(unittest.TestCase):
    """Tests for the Balance singleton: totals, transactions, reset, and observer notifications."""

    def setUp(self):
        """Get the shared Balance and reset it so every test starts at 0.0."""
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_initial_balance(self):
        """A fresh (reset) balance reads 0.0."""
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_singleton_instance(self):
        """Calling get_instance() twice returns the same object."""
        balance1 = Balance.get_instance()
        balance2 = Balance.get_instance()
        self.assertIs(balance1, balance2)

    def test_add_income(self):
        """add_income(100) raises the balance by 100."""
        self.balance.add_income(100)
        self.assertEqual(self.balance.get_balance(), 100)

    def test_add_expense(self):
        """add_expense(40) lowers the balance by 40, so it reads -40."""
        self.balance.add_expense(40)
        self.assertEqual(self.balance.get_balance(), -40)

    def test_apply_transaction_income(self):
        """An INCOME transaction of 150 raises the balance by 150."""
        t = Transaction(150, TransactionCategory.INCOME)
        self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), 150)

    def test_apply_transaction_expense(self):
        """An EXPENSE transaction of 60 lowers the balance by 60, so it reads -60."""
        t = Transaction(60, TransactionCategory.EXPENSE)
        self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), -60)

    def test_apply_transaction_invalid_category(self):
        """A transaction with an unknown category raises ValueError."""
        class FakeCategory:
            pass
        t = Transaction(100, FakeCategory())
        with self.assertRaises(ValueError):
            self.balance.apply_transaction(t)

    def test_reset(self):
        """reset() clears income and expenses back to 0.0."""
        self.balance.add_income(100)
        self.balance.add_expense(50)
        self.balance.reset()
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_summary(self):
        """summary() shows the net balance with two decimal places."""
        self.balance.add_income(1200.5)
        self.balance.add_expense(0.5)
        self.assertEqual(self.balance.summary(), "Balance: $1200.00")

    def test_direct_construction_is_blocked(self):
        """Calling Balance() directly raises RuntimeError, forcing use of get_instance()."""
        with self.assertRaises(RuntimeError):
            Balance()

    def test_apply_multiple_transactions(self):
        """Applying +200, -50, and -25 in sequence leaves the balance at 125."""
        self.balance.apply_transaction(Transaction(200, TransactionCategory.INCOME))
        self.balance.apply_transaction(Transaction(50, TransactionCategory.EXPENSE))
        self.balance.apply_transaction(Transaction(25, TransactionCategory.EXPENSE))
        self.assertEqual(self.balance.get_balance(), 125)

    def test_observer_is_notified_with_balance_and_transaction(self):
        """A registered observer gets one update containing the new balance and the transaction."""
        observer = self._register_recording_observer()
        t = Transaction(80, TransactionCategory.INCOME)

        self.balance.apply_transaction(t)

        self.assertEqual(observer.calls, [(80, t)])

    def test_observer_receives_updated_balance_after_expense(self):
        """After +100 and then -30, the observer sees balances 100 and then 70."""
        observer = self._register_recording_observer()
        self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
        self.balance.apply_transaction(Transaction(30, TransactionCategory.EXPENSE))

        self.assertEqual([balance for balance, _ in observer.calls], [100, 70])

    def test_all_registered_observers_are_notified(self):
        """Every registered observer is notified, not only the first one."""
        first = self._register_recording_observer()
        second = self._register_recording_observer()

        self.balance.apply_transaction(Transaction(10, TransactionCategory.INCOME))

        self.assertEqual(len(first.calls), 1)
        self.assertEqual(len(second.calls), 1)

    def test_registering_same_observer_twice_notifies_once(self):
        """Registering the same observer twice does not cause duplicate notifications."""
        observer = self._register_recording_observer()
        self.balance.register_observer(observer)

        self.balance.apply_transaction(Transaction(10, TransactionCategory.INCOME))

        self.assertEqual(len(observer.calls), 1)

    def test_unregistered_observer_is_not_notified(self):
        """An observer removed with unregister_observer() receives no updates."""
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        self.balance.unregister_observer(observer)

        self.balance.apply_transaction(Transaction(10, TransactionCategory.INCOME))

        self.assertEqual(observer.calls, [])

    def test_observer_not_notified_on_invalid_category(self):
        """A transaction that raises ValueError does not notify observers."""
        class FakeCategory:
            pass

        observer = self._register_recording_observer()

        with self.assertRaises(ValueError):
            self.balance.apply_transaction(Transaction(100, FakeCategory()))

        self.assertEqual(observer.calls, [])

    def test_add_income_and_add_expense_do_not_notify_observers(self):
        """The low-level add_income() and add_expense() methods do not notify observers.

        Only apply_transaction() sends notifications.
        """
        observer = self._register_recording_observer()

        self.balance.add_income(100)
        self.balance.add_expense(40)

        self.assertEqual(observer.calls, [])

    def _register_recording_observer(self):
        """Create a RecordingObserver, register it, and unregister it after the test."""
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        self.addCleanup(self.balance.unregister_observer, observer)
        return observer


if __name__ == "__main__":
    unittest.main()
