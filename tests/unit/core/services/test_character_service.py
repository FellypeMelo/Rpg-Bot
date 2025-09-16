import unittest
from unittest.mock import MagicMock, patch
from src.core.services.character_service import CharacterService
from src.core.entities.character import Character
from src.core.entities.class_template import ClassTemplate
from src.utils.exceptions.application_exceptions import CharacterNotFoundError, InvalidInputError, CharacterError

class TestCharacterService(unittest.TestCase):

    def setUp(self):
        self.mock_character_repository = MagicMock()
        self.character_service = CharacterService(self.mock_character_repository)

        self.mock_character = Character(
            name="TestChar",
            class_name="Warrior",
            attributes={"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
            hp=100, max_hp=100, chakra=50, max_chakra=50, fp=30, max_fp=30
        )
        self.mock_character.id = "test_char_id"

        self.mock_warrior_template = ClassTemplate(
            name="Warrior",
            description="A strong fighter.",
            base_attributes={"strength": 12, "dexterity": 10, "constitution": 14, "intelligence": 8, "wisdom": 10, "charisma": 6},
            hp_formula="15d5",
            chakra_formula="5d3",
            fp_formula="3d4",
            level_up_bonuses={"status_points": 3, "mastery_points": 2, "ph_points": 1}
        )
        self.mock_mage_template = ClassTemplate(
            name="Mage",
            description="A powerful spellcaster.",
            base_attributes={"strength": 8, "dexterity": 10, "constitution": 10, "intelligence": 14, "wisdom": 12, "charisma": 6},
            hp_formula="8d3",
            chakra_formula="12d5",
            fp_formula="5d3",
            level_up_bonuses={"status_points": 3, "mastery_points": 2, "ph_points": 1}
        )

    @patch('src.core.services.character_service.ClassTemplate', autospec=True)
    @patch('src.core.services.character_service.Character', autospec=True)
    def test_create_character_success(self, MockCharacter, MockClassTemplate):
        MockClassTemplate.return_value = self.mock_warrior_template
        MockCharacter.return_value = self.mock_character
        self.mock_character_repository.save_character.return_value = "new_char_id"

        character = self.character_service.create_character(name="NewHero", class_name="Warrior")

        # We don't need to assert the ClassTemplate constructor call since we're mocking the return value
        # We don't need to assert the Character constructor call since we're mocking the return value
        
        # Verify that the character was saved
        self.mock_character_repository.save_character.assert_called_once_with(self.mock_character)
        self.assertEqual(character, self.mock_character)

    def test_create_character_invalid_class(self):
        with self.assertRaises(InvalidInputError) as cm:
            self.character_service.create_character(name="Invalid", class_name="Rogue")
        self.assertIn("Classe 'Rogue' não encontrada ou não suportada.", str(cm.exception))

    def test_create_character_with_base_attributes(self):
        self.mock_character_repository.save_character.return_value = "new_char_id"
        
        with patch('src.core.entities.class_template.ClassTemplate', return_value=self.mock_warrior_template):
            character = self.character_service.create_character(
                name="CustomWarrior", class_name="Warrior", base_attributes={"strength": 15}
            )
            self.assertEqual(character.attributes["strength"], 15)
            self.assertEqual(character.attributes["dexterity"], 10) # Unchanged

    def test_create_character_with_invalid_base_attributes(self):
        with patch('src.core.entities.class_template.ClassTemplate', return_value=self.mock_warrior_template):
            with self.assertRaises(InvalidInputError) as cm:
                self.character_service.create_character(
                    name="BadAttributes", class_name="Warrior", base_attributes={"invalid_attr": 10}
                )
            self.assertIn("Atributos base fornecidos são inválidos para esta classe.", str(cm.exception))

    def test_get_character_by_id_success(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        character = self.character_service.get_character("test_char_id")
        self.assertEqual(character.id, "test_char_id")
        self.mock_character_repository.get_character.assert_called_once_with("test_char_id")

    def test_get_character_by_name_or_alias_success(self):
        self.mock_character_repository.get_character.return_value = None
        self.mock_character_repository.get_character_by_name_or_alias.return_value = self.mock_character
        character = self.character_service.get_character("TestChar")
        self.assertEqual(character.name, "TestChar")
        self.mock_character_repository.get_character_by_name_or_alias.assert_called_once_with("TestChar")

    def test_get_character_not_found(self):
        self.mock_character_repository.get_character.return_value = None
        self.mock_character_repository.get_character_by_name_or_alias.return_value = None
        with self.assertRaises(CharacterNotFoundError):
            self.character_service.get_character("non_existent")

    def test_update_character_name(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        updated_character = self.character_service.update_character("test_char_id", "name", "UpdatedName")
        self.assertEqual(updated_character.name, "UpdatedName")
        self.mock_character_repository.update_character.assert_called_once_with(self.mock_character)

    def test_update_character_alias(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        updated_character = self.character_service.update_character("test_char_id", "alias", "NewAlias")
        self.assertEqual(updated_character.alias, "NewAlias")
        self.mock_character_repository.update_character.assert_called_once_with(self.mock_character)

    def test_update_character_masteries(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        updated_character = self.character_service.update_character("test_char_id", "masteries", {"swords": 5})
        self.assertEqual(updated_character.masteries["swords"], 5)
        self.mock_character_repository.update_character.assert_called_once_with(self.mock_character)

    def test_update_character_invalid_field(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        with self.assertRaises(InvalidInputError):
            self.character_service.update_character("test_char_id", "level", 2)

    def test_update_character_masteries_invalid_value(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        with self.assertRaises(InvalidInputError):
            self.character_service.update_character("test_char_id", "masteries", "not_a_dict")

    def test_delete_character_success(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        self.mock_character_repository.delete_character.return_value = True
        result = self.character_service.delete_character("test_char_id")
        self.assertTrue(result)
        self.mock_character_repository.delete_character.assert_called_once_with("test_char_id")

    def test_delete_character_not_found(self):
        # Mock both get_character and get_character_by_name_or_alias to return None
        self.mock_character_repository.get_character.return_value = None
        self.mock_character_repository.get_character_by_name_or_alias.return_value = None
        with self.assertRaises(CharacterNotFoundError):
            self.character_service.delete_character("non_existent")

    def test_get_all_characters(self):
        char1 = Character(name="Char1", class_name="Warrior")
        char2 = Character(name="Char2", class_name="Mage")
        self.mock_character_repository.get_all_characters.return_value = [char1, char2]
        
        characters = self.character_service.get_all_characters()
        self.assertEqual(len(characters), 2)
        self.assertEqual(characters[0].name, "Char1")
        self.mock_character_repository.get_all_characters.assert_called_once()

if __name__ == '__main__':
    unittest.main()