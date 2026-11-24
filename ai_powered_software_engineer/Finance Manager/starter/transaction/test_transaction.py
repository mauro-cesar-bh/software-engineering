import unittest
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestTransaction(unittest.TestCase):
    """Tests for Transaction: its fields, text form, and equality."""

    def test_transaction_creation(self):
        """A Transaction stores the amount and category it was created with."""
        t = Transaction(100, TransactionCategory.EXPENSE)
        self.assertEqual(t.amount, 100)
        self.assertEqual(t.category, TransactionCategory.EXPENSE)

    def test_transaction_str(self):
        """str() of an INCOME transaction of 50 shows its category."""
        t = Transaction(50, TransactionCategory.INCOME)
        self.assertEqual(
            str(t), "Transaction($50, category='TransactionCategory.INCOME')"
        )

    def test_transaction_equality(self):
        """Same amount and category means equal; other amounts do not."""
        t1 = Transaction(20, TransactionCategory.EXPENSE)
        t2 = Transaction(20, TransactionCategory.EXPENSE)
        t3 = Transaction(30, TransactionCategory.EXPENSE)
        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)

    def test_transaction_str_expense(self):
        """str() of an EXPENSE transaction of 75 shows the EXPENSE category."""
        t = Transaction(75, TransactionCategory.EXPENSE)
        self.assertEqual(
            str(t), "Transaction($75, category='TransactionCategory.EXPENSE')"
        )

    def test_transaction_not_equal_when_category_differs(self):
        """Same amount but different categories means not equal."""
        income = Transaction(20, TransactionCategory.INCOME)
        expense = Transaction(20, TransactionCategory.EXPENSE)
        self.assertNotEqual(income, expense)

    def test_transaction_not_equal_to_other_types(self):
        """A Transaction is not equal to a plain number or to None."""
        t = Transaction(20, TransactionCategory.INCOME)
        self.assertNotEqual(t, 20)
        self.assertNotEqual(t, None)


if __name__ == "__main__":
    unittest.main()
