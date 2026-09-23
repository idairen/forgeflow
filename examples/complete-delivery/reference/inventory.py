"""Reference implementation for the ForgeFlow delivery tutorial (MIT)."""


class Inventory:
    def __init__(self, stock=None):
        self._stock = dict(stock or {})
        if any(type(value) is not int or value < 0 for value in self._stock.values()):
            raise ValueError("stock must contain non-negative integers")

    def snapshot(self):
        return dict(self._stock)

    def transfer(self, source, target, quantity):
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        if source == target:
            raise ValueError("source and target must differ")
        available = self._stock.get(source, 0)
        if available < quantity:
            raise ValueError("insufficient stock")
        self._stock[source] = available - quantity
        self._stock[target] = self._stock.get(target, 0) + quantity
        return self.snapshot()
