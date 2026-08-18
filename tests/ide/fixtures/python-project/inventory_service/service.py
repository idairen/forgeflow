"""Existing inventory behavior for the IDE test fixture."""


class InventoryService:
    def __init__(self, initial_stock: dict[str, int] | None = None) -> None:
        stock = initial_stock or {}
        if any(quantity < 0 for quantity in stock.values()):
            raise ValueError("initial stock cannot be negative")
        self._stock = dict(stock)

    def available(self, sku: str) -> int:
        return self._stock.get(sku, 0)

    def adjust(self, sku: str, quantity_delta: int) -> int:
        updated_quantity = self.available(sku) + quantity_delta
        if updated_quantity < 0:
            raise ValueError("stock cannot become negative")
        self._stock[sku] = updated_quantity
        return updated_quantity
