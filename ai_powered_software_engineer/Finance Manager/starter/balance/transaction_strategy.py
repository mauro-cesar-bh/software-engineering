# transaction_strategy.py
"""Strategy pattern: how a transaction changes the balance.

Each category of transaction has its own strategy object. Balance picks the
right one at run time instead of branching on the category itself.
"""


class ITransactionStrategy:
    """Interface for the rule that applies one transaction to a balance."""

    def apply(self, balance, amount) -> None:
        """Change `balance` according to this strategy's rule."""
        raise NotImplementedError("Subclasses must implement apply method.")


class IncomeStrategy(ITransactionStrategy):
    """Income increases the balance."""

    def apply(self, balance, amount) -> None:
        balance.add_income(amount)


class ExpenseStrategy(ITransactionStrategy):
    """Expenses decrease the balance."""

    def apply(self, balance, amount) -> None:
        balance.add_expense(amount)
