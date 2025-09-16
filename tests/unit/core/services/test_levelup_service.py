import unittest
from unittest.mock import MagicMock, patch
from src.core.services.levelup_service import LevelUpService
from src.core.entities.character import Character
from src.core.entities.class_template import ClassTemplate
from src.utils.exceptions.application_exceptions import LevelUpError, InvalidInputError, CharacterNotFoundError

class TestLevelUpService(unittest.TestCase):

    def setUp(self):
        self.mock_character_repository = MagicMock()
        self.levelup_service = LevelUpService(self.mock_character_repository)

        self.mock_character = Character(
            name="TestChar",
            class_name="Warrior",
            attributes={"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
            hp=100, max_hp=100, chakra=50, max_chakra=50, fp=30, max_fp=30,
            level=1, experience=0, ph_points=0, status_points=0, mastery_points=0, masteries={}
        )
        self.mock_character.id = "test_char_id"

        self.mock_warrior_template = ClassTemplate(
            name="Warrior",
            description="A strong fighter.",
            base_attributes={"strength": 12, "dexterity": 10, "constitution": 14, "intelligence": 8, "wisdom": 10, "charisma": 6},
            hp_formula="15d5",
            chakra_formula="5d3",
            fp_formula="3d4",
            starting_masteries={"swords": 2, "shields": 1},
            starting_skills=["Cleave", "Shield Bash"],
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

    @patch('src.core.entities.class_template.ClassTemplate', autospec=True)
    @patch('src.core.entities.character.Character.calculate_modifiers')
    @patch('src.core.entities.character.Character.roll_class_attributes')
    def test_apply_level_up_success(self, mock_roll_attributes, mock_calc_modifiers, MockClassTemplate):
        self.mock_character_repository.get_character.return_value = self.mock_character
        self.mock_character_repository.update_character.return_value = True
        MockClassTemplate.return_value = self.mock_warrior_template

        levels_to_gain = 1
        status_points_spent = {"strength": 2, "constitution": 1}
        mastery_points_spent = {"swords": 2}
        ph_points_spent = 1

        # Initial points before level up
        self.mock_character.status_points = 0
        self.mock_character.mastery_points = 0
        self.mock_character.ph_points = 0

        updated_character = self.levelup_service.apply_level_up(
            self.mock_character.id, levels_to_gain, status_points_spent, mastery_points_spent, ph_points_spent
        )

        self.assertEqual(updated_character.level, 2)
        self.assertEqual(updated_character.attributes["strength"], 12)
        self.assertEqual(updated_character.attributes["constitution"], 11)
        self.assertEqual(updated_character.masteries["swords"], 2)
        self.assertEqual(updated_character.ph_points, 0)
        self.assertEqual(updated_character.status_points, 0)
        self.assertEqual(updated_character.mastery_points, 0)

        mock_calc_modifiers.assert_called_once()
        mock_roll_attributes.assert_called_once_with(self.mock_warrior_template)
        self.mock_character_repository.update_character.assert_called_once_with(updated_character)

    def test_apply_level_up_character_not_found(self):
        self.mock_character_repository.get_character.return_value = None
        with self.assertRaises(CharacterNotFoundError):
            self.levelup_service.apply_level_up("non_existent_id", 1, {}, {}, 0)

    def test_apply_level_up_invalid_class(self):
        self.mock_character.class_name = "InvalidClass"
        self.mock_character_repository.get_character.return_value = self.mock_character
        with self.assertRaises(LevelUpError) as cm:
            self.levelup_service.apply_level_up(self.mock_character.id, 1, {}, {}, 0)
        self.assertIn("Classe 'InvalidClass' não encontrada ou não suportada para upagem.", str(cm.exception))

    def test_apply_level_up_exceed_status_points(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        with patch('src.core.entities.class_template.ClassTemplate', return_value=self.mock_warrior_template):
            with self.assertRaises(InvalidInputError) as cm:
                self.levelup_service.apply_level_up(self.mock_character.id, 1, {"strength": 4}, {}, 0) # 3 available
            self.assertIn("Pontos de status gastos excedem os pontos disponíveis.", str(cm.exception))

    def test_apply_level_up_exceed_mastery_points(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        with patch('src.core.entities.class_template.ClassTemplate', return_value=self.mock_warrior_template):
            with self.assertRaises(InvalidInputError) as cm:
                self.levelup_service.apply_level_up(self.mock_character.id, 1, {}, {"swords": 3}, 0) # 2 available
            self.assertIn("Pontos de maestria gastos excedem os pontos disponíveis.", str(cm.exception))

    def test_apply_level_up_exceed_ph_points(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        with patch('src.core.entities.class_template.ClassTemplate', return_value=self.mock_warrior_template):
            with self.assertRaises(InvalidInputError) as cm:
                self.levelup_service.apply_level_up(self.mock_character.id, 1, {}, {}, 2) # 1 available
            self.assertIn("Pontos de PH gastos excedem os pontos disponíveis.", str(cm.exception))

    def test_apply_level_up_negative_ph_points(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        with patch('src.core.entities.class_template.ClassTemplate', return_value=self.mock_warrior_template):
            with self.assertRaises(InvalidInputError) as cm:
                self.levelup_service.apply_level_up(self.mock_character.id, 1, {}, {}, -1)
            self.assertIn("Pontos de PH gastos não podem ser negativos.", str(cm.exception))

    def test_apply_level_up_invalid_attribute(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        with patch('src.core.entities.class_template.ClassTemplate', return_value=self.mock_warrior_template):
            with self.assertRaises(InvalidInputError) as cm:
                self.levelup_service.apply_level_up(self.mock_character.id, 1, {"invalid_attr": 1}, {}, 0)
            self.assertIn("Atributo 'invalid_attr' inválido.", str(cm.exception))

    def test_apply_level_up_accumulated_points(self):
        self.mock_character.status_points = 5 # Accumulated from previous levels
        self.mock_character.mastery_points = 3
        self.mock_character.ph_points = 2
        self.mock_character_repository.get_character.return_value = self.mock_character
        with patch('src.core.entities.class_template.ClassTemplate', return_value=self.mock_warrior_template):
            updated_character = self.levelup_service.apply_level_up(
                self.mock_character.id, 1, {"strength": 5}, {"swords": 3}, 2
            )
            self.assertEqual(updated_character.level, 2)
            self.assertEqual(updated_character.attributes["strength"], 15) # 10 (base) + 5 (spent)
            self.assertEqual(updated_character.masteries["swords"], 3)
            self.assertEqual(updated_character.ph_points, 1) # 2 (accumulated) + 1 (new) - 2 (spent)
            self.assertEqual(updated_character.status_points, 3) # 5 (accumulated) + 3 (new) - 5 (spent)
            self.assertEqual(updated_character.mastery_points, 2) # 3 (accumulated) + 2 (new) - 3 (spent)

if __name__ == '__main__':
    unittest.main()