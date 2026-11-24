import unittest
from types import SimpleNamespace

from balance.balance import Balance
from balance.transaction_strategy import (
    ExpenseStrategy,
    IncomeStrategy,
    ITransactionStrategy,
)
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class RecordingBalance:
    """Test double: a balance stand-in that records the calls it receives.

    Lets strategies be tested without the Balance singleton.
    """

    def __init__(self):
        self.calls = []

    def add_income(self, amount):
        self.calls.append(("income", amount))

    def add_expense(self, amount):
        self.calls.append(("expense", amount))


class TestStrategies(unittest.TestCase):
    """Each strategy tested alone, with no Balance singleton involved."""

    def test_income_strategy_adds_income(self):
        """IncomeStrategy calls add_income with the amount."""
        fake = RecordingBalance()
        IncomeStrategy().apply(fake, 40)
        self.assertEqual(fake.calls, [("income", 40)])

    def test_expense_strategy_adds_expense(self):
        """ExpenseStrategy calls add_expense with the amount."""
        fake = RecordingBalance()
        ExpenseStrategy().apply(fake, 25)
        self.assertEqual(fake.calls, [("expense", 25)])

    def test_strategies_share_the_interface(self):
        """Both concrete strategies are ITransactionStrategy objects."""
        self.assertIsInstance(IncomeStrategy(), ITransactionStrategy)
        self.assertIsInstance(ExpenseStrategy(), ITransactionStrategy)

    def test_base_apply_must_be_implemented(self):
        """Calling apply() on the interface raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            ITransactionStrategy().apply(RecordingBalance(), 1)


class TestBalanceUsesStrategies(unittest.TestCase):
    """Balance picks the strategy for a category at run time."""

    def setUp(self):
        """Get the shared Balance and reset it so every test starts at 0.0."""
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_new_category_without_editing_balance(self):
        """A strategy registered for a new category is used by apply_transaction."""

        class TransferOutStrategy(ITransactionStrategy):
            def apply(self, balance, amount):
                balance.add_expense(amount)

        category = "TRANSFER_OUT"
        self.balance.register_strategy(category, TransferOutStrategy())
        self.addCleanup(self.balance.unregister_strategy, category)

        self.balance.apply_transaction(SimpleNamespace(amount=30, category=category))

        self.assertEqual(self.balance.get_balance(), -30)

    def test_strategy_can_be_replaced(self):
        """Replacing a category's strategy changes how that category is applied."""

        class DoubleIncomeStrategy(ITransactionStrategy):
            def apply(self, balance, amount):
                balance.add_income(amount * 2)

        self.balance.register_strategy(
            TransactionCategory.INCOME, DoubleIncomeStrategy()
        )
        self.addCleanup(
            self.balance.register_strategy,
            TransactionCategory.INCOME,
            IncomeStrategy(),
        )

        self.balance.apply_transaction(Transaction(10, TransactionCategory.INCOME))

        self.assertEqual(self.balance.get_balance(), 20)

    def test_unregistered_category_is_invalid(self):
        """After unregister_strategy, that category raises ValueError."""
        category = "TEMP"
        self.balance.register_strategy(category, IncomeStrategy())
        self.balance.unregister_strategy(category)

        with self.assertRaises(ValueError):
            self.balance.apply_transaction(SimpleNamespace(amount=1, category=category))


if __name__ == "__main__":
    unittest.main()
