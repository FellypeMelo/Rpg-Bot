import unittest
from src.core.calculators.modifier_calc import ModifierCalculator

class TestModifierCalculator(unittest.TestCase):

    def test_calculate_modifier(self):
        self.assertEqual(ModifierCalculator.calculate_modifier(10), 2)
        self.assertEqual(ModifierCalculator.calculate_modifier(3), 0)
        self.assertEqual(ModifierCalculator.calculate_modifier(1), -1)
        self.assertEqual(ModifierCalculator.calculate_modifier(15), 4)
        self.assertEqual(ModifierCalculator.calculate_modifier(0), -1)
        self.assertEqual(ModifierCalculator.calculate_modifier(2), -1)
        self.assertEqual(ModifierCalculator.calculate_modifier(5), 0)

    def test_calculate_all_modifiers(self):
        attributes = {
            "strength": 12,
            "dexterity": 9,
            "constitution": 15,
            "intelligence": 7
        }
        expected_modifiers = {
            "strength": 3, # floor((12/3)-1) = 3
            "dexterity": 2, # floor((9/3)-1) = 2
            "constitution": 4, # floor((15/3)-1) = 4
            "intelligence": 1 # floor((7/3)-1) = 1
        }
        self.assertEqual(ModifierCalculator.calculate_all_modifiers(attributes), expected_modifiers)

    def test_calculate_all_modifiers_empty(self):
        attributes = {}
        expected_modifiers = {}
        self.assertEqual(ModifierCalculator.calculate_all_modifiers(attributes), expected_modifiers)

if __name__ == '__main__':
    unittest.main()