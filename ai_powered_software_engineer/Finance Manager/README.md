# Personal Finance Manager — Design Patterns Project

## Additional Pattern: Strategy (Student's Choice)

**Files:** `starter/balance/transaction_strategy.py`, `starter/balance/balance.py`, `starter/balance/test_transaction_strategy.py`

### Why I chose it

`Balance.apply_transaction()` decided what to do with an `if/elif` on the transaction category. This was the weakest part of the design. Every new kind of transaction (a transfer, a refund, a fee) would have meant editing `Balance`, which is also a Singleton shared by the whole app. Strategy fits this problem directly: the rule that changes the balance varies by category, so each rule becomes its own object. I picked it over Command and Decorator because the problem was already in the code and needed no new feature. The project already uses Observer on the same method, so Strategy and Observer work together without overlapping.

### Where it fits

- `ITransactionStrategy` is the interface, with one method: `apply(balance, amount)`.
- `IncomeStrategy` calls `balance.add_income()`. `ExpenseStrategy` calls `balance.add_expense()`.
- `Balance` keeps a `category -> strategy` map. `apply_transaction()` looks up the strategy, runs it, then notifies observers. An unknown category still raises `ValueError`, and observers are not notified in that case.
- `register_strategy()` and `unregister_strategy()` change the map at run time.

```
Transaction --category--> Balance._strategies[category] --apply()--> add_income / add_expense
                                                                   \-> then notify observers
```

### How it improves the design

- **Flexibility (Open/Closed):** A new category needs only a new strategy class and one `register_strategy()` call. `apply_transaction()` stays unchanged. An existing rule can also be replaced at run time.
- **Testability:** Each strategy is tested alone with a fake balance, with no Singleton and no reset (`TestStrategies`). `Balance` is tested separately with fake strategies (`TestBalanceUsesStrategies`). The tests register a new category and clean it up afterward.
- **Scalability:** Complexity grows by adding small classes, not by lengthening one conditional. Each class has a single reason to change (Single Responsibility).

All 45 tests pass, including the original Balance, Transaction, Adapter and Observer tests, which needed no changes.

## Reflection

This project uses four design patterns. Below is what each one does, how it improved the design, and the trade-offs I hit while implementing them.

### The four patterns

1. **Singleton** (`Balance.get_instance()` in `balance/balance.py`) — Every part of the app must see the same money total. A second `Balance` object would track a different number, so the class keeps one shared instance. `__init__` raises on purpose, so callers cannot create a second, diverging total with `Balance()`.

2. **Adapter** (`TransactionAdapter` in `transaction/transaction_adapter.py`) — External freelance income (`ExternalFreelanceIncome`) uses a different shape (`invoice_id`, `typ`, `description`) than the app's `Transaction`. The adapter converts that object into a standard `Transaction`. `Balance` never learns about third-party formats, and a new external source only needs a new adapter.

3. **Observer** (`IBalanceObserver`, `PrintObserver`, `LowBalanceAlertObserver` in `balance/balance_observer.py`) — After each successful transaction, `Balance` notifies subscribers without knowing what they do. Printing and low-balance alerts were added with no changes to `Balance` itself.

4. **Strategy** (`transaction_strategy.py`) — Replaced the category `if/elif` in `apply_transaction()` with a `category -> strategy` map. Income and expense each have their own rule object. New categories are added with `register_strategy()` without editing `apply_transaction()` (Open/Closed). Details are in [Additional Pattern: Strategy](#additional-pattern-strategy-students-choice) above.

### How each improved the design

| Pattern | Improvement |
| --- | --- |
| Singleton | One shared balance across the whole app; no risk of two totals drifting apart. |
| Adapter | Keeps external data formats out of the core model; new sources plug in without changing `Balance` or `Transaction`. |
| Observer | Side effects (print, alert) stay outside `Balance`; new reactions register without editing the balance logic. |
| Strategy | Balance rules become small, testable classes; `apply_transaction()` no longer grows with every new category. |

### Trade-offs encountered

- **Singleton:** Global state makes tests depend on each other, so tests need `reset()`. Blocking `__init__` and creating the object with `__new__` is less obvious than a normal constructor. Observers and strategies also live on the shared instance, so tests must clean up registrations. The implementation is not thread-safe.

- **Adapter:** `TransactionAdapter` hardcodes `TransactionCategory.INCOME` and ignores the external object's `typ` field. That is simple and correct for freelance income. A second external source that can also be an expense would need a smarter or separate adapter.

- **Observer:** Notification is synchronous, so a slow or failing observer blocks or breaks the others, and there is no ordering guarantee. Observers receive the net balance and the transaction, not the previous balance. `LowBalanceAlertObserver` keeps state (`alert_triggered`) that is reset on every update.

- **Strategy:** More small classes and indirection for only two rules. Strategies call the public `add_income` / `add_expense` methods, which keeps compatibility with the original tests but leaves those methods callable outside the strategy flow. Unknown categories raise `ValueError` at apply time, not when the `Transaction` is created.

- **Overall:** Strategy and Observer both sit on `apply_transaction()`, so ordering matters: observers fire only after a valid strategy has run. An invalid category fails before any notification.

### What I would do next

Make the adapter category-aware (or add adapters per external source), add a way to inject or fully reset `Balance` for tests (including observers and strategies), and implement the unfinished `summary()` method.

## Built With

* [Python](https://www.python.org/) – Main programming language
* [unittest](https://docs.python.org/3/library/unittest.html) – Testing framework
* [PEP8](https://peps.python.org/pep-0008/) – Style guide for Python code

## License

[License](LICENSE.txt)
