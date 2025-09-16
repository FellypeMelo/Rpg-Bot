import re
from typing import Any, Dict, Optional
from src.utils.exceptions.application_exceptions import InvalidInputError

class InputValidator:
    @staticmethod
    def validate_not_empty(value: Any, field_name: str):
        if not value:
            raise InvalidInputError(f"O campo '{field_name}' não pode ser vazio.")
        if isinstance(value, str) and not value.strip():
            raise InvalidInputError(f"O campo '{field_name}' não pode conter apenas espaços em branco.")

    @staticmethod
    def validate_string_length(value: str, field_name: str, min_length: int = 1, max_length: int = 255):
        InputValidator.validate_not_empty(value, field_name)
        if not (min_length <= len(value) <= max_length):
            raise InvalidInputError(f"O campo '{field_name}' deve ter entre {min_length} e {max_length} caracteres.")

    @staticmethod
    def validate_integer_range(value: int, field_name: str, min_value: int = 0, max_value: int = 1000000):
        if not isinstance(value, int):
            raise InvalidInputError(f"O campo '{field_name}' deve ser um número inteiro.")
        if not (min_value <= value <= max_value):
            raise InvalidInputError(f"O campo '{field_name}' deve estar entre {min_value} e {max_value}.")

    @staticmethod
    def validate_dict_not_empty(value: Dict, field_name: str):
        if not isinstance(value, dict):
            raise InvalidInputError(f"O campo '{field_name}' deve ser um dicionário.")
        if not value:
            raise InvalidInputError(f"O campo '{field_name}' não pode ser um dicionário vazio.")

    @staticmethod
    def validate_attribute_name(attribute_name: str):
        valid_attributes = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        if attribute_name.lower() not in valid_attributes:
            raise InvalidInputError(f"Atributo '{attribute_name}' inválido. Atributos válidos são: {', '.join(valid_attributes)}.")

    @staticmethod
    def validate_attribute_value(value: int, attribute_name: str):
        InputValidator.validate_integer_range(value, attribute_name, min_value=1, max_value=99) # RPG specific range

    @staticmethod
    def validate_mastery_name(mastery_name: str):
        if not re.match(r"^[a-zA-Z0-9_ ]+$", mastery_name):
            raise InvalidInputError(f"Nome de maestria '{mastery_name}' inválido. Use apenas letras, números, espaços e underscores.")
        InputValidator.validate_string_length(mastery_name, "nome da maestria", min_length=2, max_length=50)

    @staticmethod
    def validate_mastery_value(value: int, mastery_name: str):
        InputValidator.validate_integer_range(value, mastery_name, min_value=0, max_value=10) # RPG specific range

    @staticmethod
    def validate_class_name(class_name: str):
        InputValidator.validate_string_length(class_name, "nome da classe", min_length=2, max_length=50)
        if not re.match(r"^[a-zA-Z ]+$", class_name):
            raise InvalidInputError(f"Nome da classe '{class_name}' inválido. Use apenas letras e espaços.")

    @staticmethod
    def validate_character_name(name: str):
        InputValidator.validate_string_length(name, "nome do personagem", min_length=2, max_length=100)
        if not re.match(r"^[a-zA-Z0-9_ ]+$", name):
            raise InvalidInputError(f"Nome do personagem '{name}' inválido. Use apenas letras, números, espaços e underscores.")

    @staticmethod
    def validate_alias(alias: Optional[str]):
        if alias is not None:
            InputValidator.validate_string_length(alias, "apelido do personagem", min_length=2, max_length=50)
            if not re.match(r"^[a-zA-Z0-9_ ]+$", alias):
                raise InvalidInputError(f"Apelido do personagem '{alias}' inválido. Use apenas letras, números, espaços e underscores.")