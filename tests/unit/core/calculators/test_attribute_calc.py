import unittest
from unittest.mock import patch, MagicMock
from src.core.calculators.attribute_calc import AttributeCalculator
from src.core.calculators.dice_roller import DiceRoller
from src.core.entities.class_template import ClassTemplate

class TestAttributeCalculator(unittest.TestCase):

    @patch('src.core.calculators.dice_roller.DiceRoller.roll_dice')
    def test_roll_class_attributes(self, mock_roll_dice):
        mock_roll_dice.side_effect = [100, 50, 30] # Simulate HP, Chakra, FP rolls

        class_template = ClassTemplate(
            name="TestClass",
            description="A test class",
            base_attributes={},
            hp_formula="15d5",
            chakra_formula="5d3",
            fp_formula="3d4"
        )

        hp, chakra, fp = AttributeCalculator.roll_class_attributes(class_template)

        self.assertEqual(hp, 100)
        self.assertEqual(chakra, 50)
        self.assertEqual(fp, 30)

        mock_roll_dice.assert_any_call("15d5")
        mock_roll_dice.assert_any_call("5d3")
        mock_roll_dice.assert_any_call("3d4")
        self.assertEqual(mock_roll_dice.call_count, 3)

    @patch('src.core.calculators.dice_roller.DiceRoller.roll_dice')
    def test_roll_class_attributes_with_default_formulas(self, mock_roll_dice):
        mock_roll_dice.side_effect = [1, 1, 1] # Simulate default rolls

        class_template = ClassTemplate(
            name="DefaultClass",
            description="A default test class",
            base_attributes={},
            hp_formula="1d1", # Default value
            chakra_formula="1d1", # Default value
            fp_formula="1d1" # Default value
        )

        hp, chakra, fp = AttributeCalculator.roll_class_attributes(class_template)

        self.assertEqual(hp, 1)
        self.assertEqual(chakra, 1)
        self.assertEqual(fp, 1)

        mock_roll_dice.assert_any_call("1d1")
        self.assertEqual(mock_roll_dice.call_count, 3)

if __name__ == '__main__':
    unittest.main()