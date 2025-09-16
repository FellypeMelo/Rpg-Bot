import unittest
from unittest.mock import patch
from src.core.calculators.dice_roller import DiceRoller

class TestDiceRoller(unittest.TestCase):

    @patch('random.randint')
    def test_roll_dice_simple(self, mock_randint):
        mock_randint.side_effect = [3] # Simulate rolling a 3 on a 1d6
        self.assertEqual(DiceRoller.roll_dice("1d6"), 3)
        mock_randint.assert_called_once_with(1, 6)

    @patch('random.randint')
    def test_roll_dice_multiple(self, mock_randint):
        mock_randint.side_effect = [2, 4, 6] # Simulate rolling 2, 4, 6 on 3d6
        self.assertEqual(DiceRoller.roll_dice("3d6"), 12)
        self.assertEqual(mock_randint.call_count, 3)
        mock_randint.assert_called_with(1, 6)

    @patch('random.randint')
    def test_roll_dice_with_positive_modifier(self, mock_randint):
        mock_randint.side_effect = [5] # Simulate rolling a 5 on 1d10+2
        self.assertEqual(DiceRoller.roll_dice("1d10+2"), 7)
        mock_randint.assert_called_once_with(1, 10)

    @patch('random.randint')
    def test_roll_dice_with_negative_modifier(self, mock_randint):
        mock_randint.side_effect = [8] # Simulate rolling an 8 on 1d12-3
        self.assertEqual(DiceRoller.roll_dice("1d12-3"), 5)
        mock_randint.assert_called_once_with(1, 12)

    @patch('random.randint')
    def test_roll_dice_no_num_dice_specified(self, mock_randint):
        mock_randint.side_effect = [4] # Simulate rolling a 4 on d8 (defaults to 1d8)
        self.assertEqual(DiceRoller.roll_dice("d8"), 4)
        mock_randint.assert_called_once_with(1, 8)

    def test_roll_dice_invalid_notation(self):
        with self.assertRaises(ValueError) as cm:
            DiceRoller.roll_dice("invalid_notation")
        self.assertIn("Notação de dado inválida", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            DiceRoller.roll_dice("0d6")
        self.assertIn("Número de dados e lados devem ser maiores que zero", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            DiceRoller.roll_dice("1d0")
        self.assertIn("Número de dados e lados devem ser maiores que zero", str(cm.exception))

if __name__ == '__main__':
    unittest.main()