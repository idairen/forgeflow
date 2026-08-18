import unittest

from inventory_service import InventoryService


class InventoryServiceTests(unittest.TestCase):
    def test_unknown_sku_has_zero_stock(self) -> None:
        service = InventoryService()

        self.assertEqual(service.available("SKU-1"), 0)

    def test_adjust_updates_available_stock(self) -> None:
        service = InventoryService({"SKU-1": 5})

        self.assertEqual(service.adjust("SKU-1", -2), 3)
        self.assertEqual(service.available("SKU-1"), 3)

    def test_adjust_rejects_negative_stock(self) -> None:
        service = InventoryService({"SKU-1": 1})

        with self.assertRaisesRegex(ValueError, "stock cannot become negative"):
            service.adjust("SKU-1", -2)


if __name__ == "__main__":
    unittest.main()
