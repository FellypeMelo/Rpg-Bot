from typing import Dict, Optional
from src.application.dtos.character_dto import CreateCharacterDTO, UpdateCharacterDTO
from src.application.validators.input_validators import InputValidator
from src.utils.exceptions.application_exceptions import InvalidInputError

class CharacterValidator:
    @staticmethod
    def validate_create_character_dto(dto: CreateCharacterDTO):
        InputValidator.validate_character_name(dto.name)
        InputValidator.validate_class_name(dto.class_name)
        InputValidator.validate_alias(dto.alias)
        
        if dto.base_attributes:
            InputValidator.validate_dict_not_empty(dto.base_attributes, "atributos base")
            for attr, value in dto.base_attributes.items():
                InputValidator.validate_attribute_name(attr)
                InputValidator.validate_attribute_value(value, attr)

    @staticmethod
    def validate_update_character_dto(dto: UpdateCharacterDTO):
        InputValidator.validate_not_empty(dto.character_id, "ID do personagem")
        InputValidator.validate_not_empty(dto.field_name, "nome do campo")

        if dto.field_name == "name":
            InputValidator.validate_character_name(dto.value)
        elif dto.field_name == "alias":
            InputValidator.validate_alias(dto.value)
        elif dto.field_name == "masteries":
            InputValidator.validate_dict_not_empty(dto.value, "masteries")
            for mastery, value in dto.value.items():
                InputValidator.validate_mastery_name(mastery)
                InputValidator.validate_mastery_value(value, mastery)
        else:
            raise InvalidInputError(f"O campo '{dto.field_name}' não pode ser atualizado diretamente.")