# Personal Finance Manager — Design Patterns Project

This project is a hands-on exercise in applying Object-Oriented Design Patterns to build a simplified personal finance manager.
You will implement and extend starter code to add functionality such as tracking transactions, adapting external data, observing balance changes, and ensuring proper architectural patterns.

## Getting Started

### Dependencies

Make sure you have python version >= 3.10.x installed on your computer. 


### Installation

1. Clone the repo:

```
bash
git clone https://github.com/udacity/cd14600-project-starter.git
cd cd14600-project-starter/starter
```

2. Run the Program: 
```
python main.py
```

## Testing

This project uses Python’s built-in unittest framework.

To run all tests:

```
python -m unittest discover
```

To run a single test file:
```
python -m unittest balance/test_balance_observer.py
```

### Break Down Tests

- test_balance.py → Verifies correct implementation of the Singleton Balance class.
- test_transaction.py → Confirms transactions update balances correctly.
- test_transaction_adapter.py → Ensures external income data is correctly adapted into Transaction objects.
- test_balance_observer.py → Validates that low-balance alerts are triggered at the correct threshold.

## Project Instructions

1. Implement Singleton Balance Class – Ensure only one balance object exists throughout the app.
2. Complete Transaction Class – Handle income and expense transactions.
3. Implement Adapter Pattern – Adapt external freelance income data into internal Transaction objects.
4. Implement Observer Pattern – Create a low balance observer that triggers an alert when funds drop too low.
5. Add Unit Tests – Write tests for all implemented functionality.
6. Choose and Implement a Fourth Pattern – Pick one additional design pattern (e.g., Strategy, Command, Decorator, etc.) and integrate it into your project.
7. Provide a Reflection – Add a short write-up in your repo (README or separate file) explaining your design choices.

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

## Built With

* [Python](https://www.python.org/) – Main programming language
* [unittest](https://docs.python.org/3/library/unittest.html) – Testing framework
* [PEP8](https://peps.python.org/pep-0008/) – Style guide for Python code

## License

[License](LICENSE.txt)
