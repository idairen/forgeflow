# Inventory Service IDE Test Fixture

This is a deliberately small existing Python project for ForgeFlow IDE acceptance testing.

The baseline supports stock lookup and controlled stock adjustment. Reservation,
release, idempotency, and audit behavior are intentionally absent so the ForgeFlow
workflows have real delivery work to define and implement.

Run the baseline tests with:

```bash
python3 -m unittest discover -s tests -v
```
