from typing import Dict
from src.core.entities.character import Character
from src.core.entities.class_template import ClassTemplate
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.core.calculators.modifier_calc import ModifierCalculator
from src.core.calculators.attribute_calc import AttributeCalculator
from src.utils.exceptions.application_exceptions import LevelUpError, InvalidInputError, CharacterNotFoundError

class LevelUpService:
    def __init__(self, character_repository: MongoDBRepository):
        self.character_repository = character_repository

    def apply_level_up(self, character_id: str, levels_to_gain: int, status_points_spent: Dict[str, int], mastery_points_spent: Dict[str, int], ph_points_spent: int) -> Character:
        character = self.character_repository.get_character(character_id)
        if not character:
            raise CharacterNotFoundError(f"Personagem com ID '{character_id}' não encontrado.")

        # For now, we'll use a dummy ClassTemplate. In a real scenario, this would be fetched from a repository.
        # This is a placeholder for RN-01.
        from config.constants.game_constants import DEFAULT_CLASS_TEMPLATES
        class_template_data = DEFAULT_CLASS_TEMPLATES.get(character.class_name)
        if not class_template_data:
            raise LevelUpError(f"Classe '{character.class_name}' não encontrada ou não suportada para upagem.")
        
        class_template = ClassTemplate(**class_template_data)

        # Calculate total points gained from levels
        total_status_points_gained = levels_to_gain * class_template.level_up_bonuses["status_points"]
        total_mastery_points_gained = levels_to_gain * class_template.level_up_bonuses["mastery_points"]
        total_ph_points_gained = levels_to_gain * class_template.level_up_bonuses["ph_points"]

        # Add accumulated unused points
        total_status_points_available = character.status_points + total_status_points_gained
        total_mastery_points_available = character.mastery_points + total_mastery_points_gained
        total_ph_points_available = character.ph_points + total_ph_points_gained

        # Validate points spent
        if sum(status_points_spent.values()) > total_status_points_available:
            raise InvalidInputError("Pontos de status gastos excedem os pontos disponíveis.")
        if sum(mastery_points_spent.values()) > total_mastery_points_available:
            raise InvalidInputError("Pontos de maestria gastos excedem os pontos disponíveis.")
        if ph_points_spent > total_ph_points_available:
            raise InvalidInputError("Pontos de PH gastos excedem os pontos disponíveis.")
        if ph_points_spent < 0:
            raise InvalidInputError("Pontos de PH gastos não podem ser negativos.")

        # Apply points
        for attr, points in status_points_spent.items():
            if attr not in character.attributes:
                raise InvalidInputError(f"Atributo '{attr}' inválido.")
            character.attributes[attr] += points
        
        for mastery, points in mastery_points_spent.items():
            character.masteries[mastery] = character.masteries.get(mastery, 0) + points
        
        character.ph_points = total_ph_points_available - ph_points_spent
        character.status_points = total_status_points_available - sum(status_points_spent.values())
        character.mastery_points = total_mastery_points_available - sum(mastery_points_spent.values())

        # Update level
        for _ in range(levels_to_gain):
            character.level += 1
            character.roll_class_attributes(class_template, add_to_existing=True) # Re-roll HP/Chakra/FP based on new level/attributes

        # Recalculate modifiers
        character.calculate_modifiers()

        self.character_repository.update_character(character)
        return character