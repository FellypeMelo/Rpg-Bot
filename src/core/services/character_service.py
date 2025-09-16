from typing import Optional, Dict, Any, List
from src.core.entities.character import Character
from src.core.entities.class_template import ClassTemplate
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.core.calculators.attribute_calc import AttributeCalculator
from src.core.calculators.modifier_calc import ModifierCalculator
from src.utils.exceptions.application_exceptions import CharacterNotFoundError, InvalidInputError, CharacterError

class CharacterService:
    def __init__(self, character_repository: MongoDBRepository):
        self.character_repository = character_repository

    def create_character(self, name: str, class_name: str, alias: Optional[str] = None, base_attributes: Optional[Dict[str, int]] = None) -> Character:
        # For now, we'll use a dummy ClassTemplate. In a real scenario, this would be fetched from a repository.
        # For now, we'll use a dummy ClassTemplate. In a real scenario, this would be fetched from a repository.
        # This is a placeholder for RF-01 and RF-07.
        # Using a dictionary for class templates for now, will refactor to a repository later.
        from config.constants.game_constants import DEFAULT_CLASS_TEMPLATES
        class_template_data = DEFAULT_CLASS_TEMPLATES.get(class_name)
        if not class_template_data:
            raise InvalidInputError(f"Classe '{class_name}' não encontrada ou não suportada.")
        
        class_template = ClassTemplate(**class_template_data)

        if base_attributes:
            # Validate base_attributes if provided
            if not all(attr in class_template.base_attributes for attr in base_attributes):
                raise InvalidInputError("Atributos base fornecidos são inválidos para esta classe.")
            # Merge provided base_attributes with class_template's base_attributes
            initial_attributes = {**class_template.base_attributes, **base_attributes}
        else:
            initial_attributes = class_template.base_attributes

        character = Character(
            name=name,
            class_name=class_name,
            alias=alias,
            attributes=initial_attributes,
            status_points=class_template.level_up_bonuses["status_points"],
            mastery_points=class_template.level_up_bonuses["mastery_points"],
            ph_points=class_template.level_up_bonuses["ph_points"]
        )

        character.calculate_modifiers()
        character.roll_class_attributes(class_template, add_to_existing=False)

        self.character_repository.save_character(character)
        return character

    def get_character(self, identifier: str) -> Character:
        character = self.character_repository.get_character(identifier)
        if not character:
            character = self.character_repository.get_character_by_name_or_alias(identifier)
        if not character:
            raise CharacterNotFoundError(f"Personagem com ID/nome/apelido '{identifier}' não encontrado.")
        return character

    def update_character(self, character_id: str, field_name: str, value: Any) -> Character:
        character = self.get_character(character_id)
        
        if field_name == "name":
            character.name = value
        elif field_name == "alias":
            character.alias = value
        elif field_name == "masteries":
            if not isinstance(value, dict):
                raise InvalidInputError("Masteries devem ser um dicionário.")
            character.masteries.update(value)
        else:
            raise InvalidInputError(f"Campo '{field_name}' não pode ser atualizado diretamente.")
        
        self.character_repository.update_character(character)
        return character

    def delete_character(self, character_id: str) -> bool:
        character = self.get_character(character_id) # Ensure character exists before attempting deletion
        return self.character_repository.delete_character(character.id)

    def get_all_characters(self) -> List[Character]:
        return self.character_repository.get_all_characters()