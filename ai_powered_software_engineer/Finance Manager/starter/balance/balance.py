# balance.py

from __future__ import annotations

from balance.transaction_strategy import ExpenseStrategy, IncomeStrategy
from transaction.transaction_category import TransactionCategory


class Balance:
    """One shared balance for the whole app (Singleton).

    Every part of the program must see the same money total. A second
    Balance object would track a different total, so this class keeps a
    single object and hands that same object out every time.
    """

    # Stored on the class, not on an object, so there is only one slot.
    # None means "not created yet". After the first get_instance() call,
    # this holds the only Balance object.
    _instance: Balance | None = None

    def __init__(self) -> None:
        """Block Balance(). Call get_instance() instead."""
        # Balance() would run this method and could create extra objects.
        # Raising here forces every caller through get_instance().
        raise RuntimeError("Use Balance.get_instance() to access the balance.")

    @classmethod
    def get_instance(cls) -> Balance:
        """Return the one Balance, creating it the first time.

        A classmethod receives the class (cls) instead of an object (self),
        so it can read and fill the shared _instance slot.
        """
        if cls._instance is None:
            # __new__ allocates the object but does not call __init__.
            # That matters: __init__ raises on purpose, so we cannot write
            # Balance() here.
            instance = cls.__new__(cls)
            # A brand-new account starts with no money.
            instance._net_balance = 0.0

            # No one is subscribed yet.
            instance._observers = []

            # Strategy pattern: one rule per transaction category.
            instance._strategies = {
                TransactionCategory.INCOME: IncomeStrategy(),
                TransactionCategory.EXPENSE: ExpenseStrategy(),
            }

            # Save it so the next call returns this same object.
            cls._instance = instance
        return cls._instance

    def reset(self) -> None:
        """Set the net balance back to zero."""
        self._net_balance = 0.0

    def add_income(self, amount):
        """Add income to the balance."""
        self._net_balance = self._net_balance + amount

    def add_expense(self, amount):
        """Subtract expense from the balance."""
        self._net_balance = self._net_balance - amount

    def apply_transaction(self, transaction):
        """
        Apply a Transaction object to update the balance.

        Args:
            transaction (Transaction): The transaction to apply.
        """
        strategy = self._strategies.get(transaction.category)
        if strategy is None:
            raise ValueError(
                f"Invalid transaction category: {transaction.category}"
            )

        strategy.apply(self, transaction.amount)
        self._notify_observers(transaction)

    def register_strategy(self, category, strategy) -> None:
        """Set the strategy used for a transaction category.

        Adds support for a new category, or replaces the rule of an
        existing one, without editing apply_transaction().
        """
        self._strategies[category] = strategy

    def unregister_strategy(self, category) -> None:
        """Remove a category's strategy, making it invalid."""
        del self._strategies[category]

    def get_balance(self) -> float:
        """Return the current net balance.

        Income makes this number larger. Expenses make it smaller.
        A fresh or reset balance is 0.0.
        """
        return self._net_balance

    def summary(self) -> str:
        """Return a one-line summary of the current net balance."""
        return f"Balance: ${self._net_balance:.2f}"

    def register_observer(self, observer) -> None:
        """Subscribe an observer to balance changes."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer) -> None:
        """Unsubscribe an observer."""
        self._observers.remove(observer)

    def _notify_observers(self, transaction) -> None:
        for observer in self._observers:
            observer.update(self._net_balance, transaction)
