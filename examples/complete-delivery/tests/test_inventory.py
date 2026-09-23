import unittest

from inventory import Inventory


class InventoryAcceptanceTests(unittest.TestCase):
    def test_success_moves_exact_quantity_and_conserves_total(self):
        inventory = Inventory({"A": 5, "B": 2})
        self.assertEqual(inventory.transfer("A", "B", 3), {"A": 2, "B": 5})
        self.assertEqual(sum(inventory.snapshot().values()), 7)

    def test_insufficient_stock_leaves_every_balance_unchanged(self):
        inventory = Inventory({"A": 2, "B": 3})
        before = inventory.snapshot()
        with self.assertRaisesRegex(ValueError, "insufficient stock"):
            inventory.transfer("A", "B", 4)
        self.assertEqual(inventory.snapshot(), before)

    def test_unknown_source_does_not_create_a_balance(self):
        inventory = Inventory({"B": 3})
        with self.assertRaisesRegex(ValueError, "insufficient stock"):
            inventory.transfer("missing", "B", 1)
        self.assertEqual(inventory.snapshot(), {"B": 3})

    def test_new_destination_is_created_on_success(self):
        inventory = Inventory({"A": 2})
        self.assertEqual(inventory.transfer("A", "B", 2), {"A": 0, "B": 2})

    def test_invalid_quantity_never_mutates_stock(self):
        for quantity in (0, -1, 1.5, True, "1", None):
            with self.subTest(quantity=quantity):
                inventory = Inventory({"A": 5})
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    inventory.transfer("A", "B", quantity)
                self.assertEqual(inventory.snapshot(), {"A": 5})

    def test_same_location_never_mutates_stock(self):
        inventory = Inventory({"A": 5})
        with self.assertRaisesRegex(ValueError, "must differ"):
            inventory.transfer("A", "A", 2)
        self.assertEqual(inventory.snapshot(), {"A": 5})

    def test_snapshot_cannot_mutate_inventory(self):
        inventory = Inventory({"A": 5})
        result = inventory.transfer("A", "B", 1)
        result["A"] = 100
        self.assertEqual(inventory.snapshot(), {"A": 4, "B": 1})

    def test_invalid_initial_stock_is_rejected(self):
        for quantity in (-1, 1.5, True):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                Inventory({"A": quantity})


if __name__ == "__main__":
    unittest.main()
