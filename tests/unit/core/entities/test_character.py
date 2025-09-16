import unittest
from datetime import datetime, timedelta, timezone
from src.core.entities.character import Character
from src.core.entities.class_template import ClassTemplate
from unittest.mock import patch, MagicMock

class TestCharacter(unittest.TestCase):

    def setUp(self):
        self.character_data = {
            "name": "Test Character",
            "class_name": "Warrior",
            "attributes": {
                "strength": 12, "dexterity": 10, "constitution": 14,
                "intelligence": 8, "wisdom": 10, "charisma": 6
            },
            "hp": 100, "max_hp": 100,
            "chakra": 50, "max_chakra": 50,
            "fp": 30, "max_fp": 30,
        }
        self.character = Character(**self.character_data)

    def test_character_creation(self):
        self.assertIsNotNone(self.character.id)
        self.assertEqual(self.character.name, "Test Character")
        self.assertEqual(self.character.class_name, "Warrior")
        self.assertEqual(self.character.level, 1)
        self.assertEqual(self.character.experience, 0)
        self.assertEqual(self.character.attributes["strength"], 12)
        self.assertEqual(self.character.hp, 100)
        self.assertIsInstance(datetime.fromisoformat(self.character.created_at), datetime)
        self.assertIsInstance(datetime.fromisoformat(self.character.updated_at), datetime)

    def test_to_dict_method(self):
        char_dict = self.character.to_dict()
        self.assertIsInstance(char_dict, dict)
        self.assertEqual(char_dict["name"], "Test Character")
        self.assertEqual(char_dict["id"], self.character.id)
        self.assertIn("attributes", char_dict)
        self.assertIn("created_at", char_dict)

    def test_from_dict_method(self):
        char_dict = self.character.to_dict()
        new_character = Character.from_dict(char_dict)
        self.assertEqual(new_character.id, self.character.id)
        self.assertEqual(new_character.name, self.character.name)
        self.assertEqual(new_character.class_name, self.character.class_name)
        self.assertEqual(new_character.level, self.character.level)
        self.assertEqual(new_character.attributes["strength"], self.character.attributes["strength"])

    @patch('src.core.calculators.modifier_calc.ModifierCalculator.calculate_all_modifiers')
    def test_calculate_modifiers(self, mock_calculate_all_modifiers):
        mock_calculate_all_modifiers.return_value = {"strength": 1, "dexterity": 0, "constitution": 1, "intelligence": -1, "wisdom": 0, "charisma": -2}
        self.character.calculate_modifiers()
        mock_calculate_all_modifiers.assert_called_once_with(self.character.attributes)
        self.assertEqual(self.character.modifiers["strength"], 1)

    @patch('src.core.calculators.attribute_calc.AttributeCalculator.roll_class_attributes')
    def test_roll_class_attributes(self, mock_roll_class_attributes):
        mock_roll_class_attributes.return_value = (120, 60, 40)
        class_template = ClassTemplate(name="Warrior", description="A strong fighter")
        self.character.roll_class_attributes(class_template)
        mock_roll_class_attributes.assert_called_once_with(class_template)
        self.assertEqual(self.character.hp, 120)
        self.assertEqual(self.character.max_hp, 120)
        self.assertEqual(self.character.chakra, 60)
        self.assertEqual(self.character.max_chakra, 60)
        self.assertEqual(self.character.fp, 40)
        self.assertEqual(self.character.max_fp, 40)

    def test_apply_damage_hp(self):
        initial_hp = self.character.hp
        self.character.apply_damage("hp", 20)
        self.assertEqual(self.character.hp, initial_hp - 20)
        # Ensure we're comparing timezone-aware datetimes
        self.assertGreater(datetime.fromisoformat(self.character.updated_at), 
                          datetime.min.replace(tzinfo=timezone.utc))

    def test_apply_damage_hp_below_zero(self):
        self.character.apply_damage("hp", 150)
        self.assertEqual(self.character.hp, 0)

    def test_apply_damage_chakra(self):
        initial_chakra = self.character.chakra
        self.character.apply_damage("chakra", 10)
        self.assertEqual(self.character.chakra, initial_chakra - 10)

    def test_apply_damage_fp(self):
        initial_fp = self.character.fp
        self.character.apply_damage("fp", 5)
        self.assertEqual(self.character.fp, initial_fp - 5)

    def test_apply_healing_hp(self):
        self.character.hp = 50
        self.character.apply_healing("hp", 30)
        self.assertEqual(self.character.hp, 80)
        # Ensure we're comparing timezone-aware datetimes
        self.assertGreater(datetime.fromisoformat(self.character.updated_at), 
                          datetime.min.replace(tzinfo=timezone.utc))

    def test_apply_healing_hp_above_max(self):
        self.character.hp = 90
        self.character.apply_healing("hp", 30)
        self.assertEqual(self.character.hp, self.character.max_hp)

    def test_apply_healing_chakra(self):
        self.character.chakra = 20
        self.character.apply_healing("chakra", 20)
        self.assertEqual(self.character.chakra, 40)

    def test_apply_healing_fp(self):
        self.character.fp = 10
        self.character.apply_healing("fp", 15)
        self.assertEqual(self.character.fp, 25)

if __name__ == '__main__':
    unittest.main()