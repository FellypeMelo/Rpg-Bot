import unittest
from src.core.entities.class_template import ClassTemplate
from typing import Dict, List, Any

class TestClassTemplate(unittest.TestCase):

    def setUp(self):
        self.class_template_data = {
            "name": "Warrior",
            "description": "A strong fighter with high HP.",
            "base_attributes": {
                "strength": 14, "dexterity": 10, "constitution": 12,
                "intelligence": 8, "wisdom": 10, "charisma": 6
            },
            "hp_formula": "15d5",
            "chakra_formula": "5d3",
            "fp_formula": "3d4",
            "starting_masteries": {"swords": 2, "shields": 1},
            "starting_skills": ["Cleave", "Shield Bash"],
            "starting_spells": [],
            "level_up_bonuses": {
                "status_points": 3,
                "mastery_points": 2,
                "ph_points": 1
            }
        }
        self.class_template = ClassTemplate(**self.class_template_data)

    def test_class_template_creation(self):
        self.assertEqual(self.class_template.name, "Warrior")
        self.assertEqual(self.class_template.description, "A strong fighter with high HP.")
        self.assertEqual(self.class_template.base_attributes["strength"], 14)
        self.assertEqual(self.class_template.hp_formula, "15d5")
        self.assertEqual(self.class_template.starting_masteries["swords"], 2)
        self.assertIn("Cleave", self.class_template.starting_skills)
        self.assertEqual(self.class_template.level_up_bonuses["status_points"], 3)

    def test_to_dict_method(self):
        template_dict = self.class_template.to_dict()
        self.assertIsInstance(template_dict, dict)
        self.assertEqual(template_dict["name"], "Warrior")
        self.assertIn("base_attributes", template_dict)
        self.assertIn("level_up_bonuses", template_dict)

    def test_from_dict_method(self):
        template_dict = self.class_template.to_dict()
        new_template = ClassTemplate.from_dict(template_dict)
        self.assertEqual(new_template.name, self.class_template.name)
        self.assertEqual(new_template.description, self.class_template.description)
        self.assertEqual(new_template.hp_formula, self.class_template.hp_formula)
        self.assertEqual(new_template.level_up_bonuses["ph_points"], self.class_template.level_up_bonuses["ph_points"])

    def test_default_values(self):
        minimal_template = ClassTemplate(name="Rogue", description="A stealthy attacker.")
        self.assertEqual(minimal_template.hp_formula, "1d1")
        self.assertEqual(minimal_template.level_up_bonuses["status_points"], 3)
        self.assertEqual(minimal_template.base_attributes["strength"], 10)

if __name__ == '__main__':
    unittest.main()