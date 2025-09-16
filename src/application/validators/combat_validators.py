from src.application.dtos.combat_dto import StartCombatSessionDTO, ApplyDamageHealingDTO, EndCombatSessionDTO
from src.application.validators.input_validators import InputValidator
from src.utils.exceptions.application_exceptions import InvalidInputError

class CombatValidator:
    @staticmethod
    def validate_start_combat_session_dto(dto: StartCombatSessionDTO):
        InputValidator.validate_not_empty(dto.character_id, "ID do personagem")
        InputValidator.validate_not_empty(dto.guild_id, "ID do servidor (guild)")
        InputValidator.validate_not_empty(dto.channel_id, "ID do canal")
        InputValidator.validate_not_empty(dto.player_id, "ID do jogador")

    @staticmethod
    def validate_apply_damage_healing_dto(dto: ApplyDamageHealingDTO):
        InputValidator.validate_not_empty(dto.session_id, "ID da sessão de combate")
        InputValidator.validate_not_empty(dto.attribute_type, "tipo de atributo")
        InputValidator.validate_integer_range(dto.value, "valor", min_value=1)

        valid_attribute_types = ["hp", "chakra", "fp"]
        if dto.attribute_type.lower() not in valid_attribute_types:
            raise InvalidInputError(f"Tipo de atributo '{dto.attribute_type}' inválido. Use 'hp', 'chakra' ou 'fp'.")

    @staticmethod
    def validate_end_combat_session_dto(dto: EndCombatSessionDTO):
        InputValidator.validate_not_empty(dto.session_id, "ID da sessão de combate")
        # persist_changes is a boolean, no further validation needed beyond type checking if it were an input string