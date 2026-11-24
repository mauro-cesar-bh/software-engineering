import unittest
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction_adapter import TransactionAdapter
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestTransactionAdapter(unittest.TestCase):
    """Tests that TransactionAdapter converts an ExternalFreelanceIncome into a standard Transaction."""

    def test_adapter_converts_freelance_income(self):
        """A 500 freelance invoice becomes a Transaction of 500 with category INCOME."""
        ext_txn = ExternalFreelanceIncome(500, "INV-12345", "Website development")
        adapter = TransactionAdapter(ext_txn)
        txn = adapter.to_transaction()
        self.assertEqual(txn, Transaction(500, TransactionCategory.INCOME))

    def test_adapter_returns_transaction_instance(self):
        """to_transaction() returns a Transaction object, not the external object."""
        ext_txn = ExternalFreelanceIncome(250, "INV-1", "Logo design")
        txn = TransactionAdapter(ext_txn).to_transaction()
        self.assertIsInstance(txn, Transaction)

    def test_adapter_always_maps_to_income(self):
        """Freelance income is always converted to the INCOME category."""
        ext_txn = ExternalFreelanceIncome(75, "INV-2", "Consulting")
        txn = TransactionAdapter(ext_txn).to_transaction()
        self.assertEqual(txn.category, TransactionCategory.INCOME)

    def test_adapter_preserves_amount(self):
        """The decimal amount 1200.5 is copied to the new Transaction unchanged."""
        ext_txn = ExternalFreelanceIncome(1200.5, "INV-98765", "Mobile App Project")
        txn = TransactionAdapter(ext_txn).to_transaction()
        self.assertEqual(txn.amount, 1200.5)


if __name__ == "__main__":
    unittest.main()
