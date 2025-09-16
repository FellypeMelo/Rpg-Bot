import unittest
from unittest.mock import MagicMock
from src.core.services.report_service import ReportService
from src.core.entities.character import Character
from src.utils.exceptions.application_exceptions import CharacterNotFoundError

class TestReportService(unittest.TestCase):

    def setUp(self):
        self.mock_character_repository = MagicMock()
        self.report_service = ReportService(self.mock_character_repository)

        self.mock_character = Character(
            name="TestChar",
            class_name="Warrior",
            attributes={"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
            hp=100, max_hp=100, chakra=50, max_chakra=50, fp=30, max_fp=30,
            level=5, experience=1200, ph_points=3, status_points=2, mastery_points=1, masteries={"swords": 2}
        )
        self.mock_character.id = "test_char_id"
        self.mock_character.calculate_modifiers() # Ensure modifiers are calculated

    def test_get_progress_report_success(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        
        report = self.report_service.get_progress_report(self.mock_character.id)

        self.assertIsNotNone(report)
        self.assertEqual(report["character_name"], "TestChar")
        self.assertEqual(report["level"], 5)
        self.assertEqual(report["hp"], "100/100")
        self.assertEqual(report["masteries"]["swords"], 2)
        self.mock_character_repository.get_character.assert_called_once_with(self.mock_character.id)

    def test_get_progress_report_character_not_found(self):
        self.mock_character_repository.get_character.return_value = None
        with self.assertRaises(CharacterNotFoundError):
            self.report_service.get_progress_report("non_existent_id")

    def test_get_usage_statistics_no_characters(self):
        self.mock_character_repository.get_all_characters.return_value = []
        stats = self.report_service.get_usage_statistics()
        self.assertEqual(stats["total_characters"], 0)
        self.assertEqual(stats["average_character_level"], 0)
        self.assertEqual(stats["class_distribution"], {})
        self.mock_character_repository.get_all_characters.assert_called_once()

    def test_get_usage_statistics_with_characters(self):
        char1 = Character(name="Char1", class_name="Warrior", level=5)
        char2 = Character(name="Char2", class_name="Mage", level=3)
        char3 = Character(name="Char3", class_name="Warrior", level=7)
        self.mock_character_repository.get_all_characters.return_value = [char1, char2, char3]

        stats = self.report_service.get_usage_statistics()
        self.assertEqual(stats["total_characters"], 3)
        self.assertEqual(stats["class_distribution"], {"Warrior": 2, "Mage": 1})
        self.assertEqual(stats["average_character_level"], round((5+3+7)/3, 2))
        self.mock_character_repository.get_all_characters.assert_called_once()

if __name__ == '__main__':
    unittest.main()