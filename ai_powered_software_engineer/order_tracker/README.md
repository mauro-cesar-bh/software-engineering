# Udatracker Starter Code

## Reflection
- **Design trade-off:** I kept business rules in `OrderTracker` and left Flask routes thin—parse JSON, call the tracker, map exceptions to HTTP status codes. That made unit tests easy with mocks, but the API had to convert storage’s order dict into a JSON list so the frontend and integration tests could index results.

- **Testing insight:** `test_list_orders_by_status_api_matching` failed when I registered a separate route like `/api/orders?status=...`. Flask ignores query strings in route paths, so filter requests hit “list all” instead. Fixing that into one GET handler that reads `request.args.get("status")` also forced returning `list(orders.values())` instead of a dict.

- **Next step:** I’d add persistent storage (e.g. SQLite or a small database) and a `DELETE /api/orders/<order_id>` endpoint, plus stricter validation for status values and required fields across every route.



## Tree Structure
The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```
