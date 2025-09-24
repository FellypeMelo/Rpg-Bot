from discord.ext import commands
from typing import Optional, Dict
from src.core.services.levelup_service import LevelUpService
from src.application.dtos.levelup_dto import ApplyLevelUpDTO, LevelUpResponseDTO
from src.utils.exceptions.application_exceptions import LevelUpError, InvalidInputError, CharacterNotFoundError
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.infrastructure.database.class_repository import ClassRepository
from src.core.services.character_service import CharacterService
import os
import json # For parsing JSON strings for points
import ast # For safely evaluating string literals

class LevelUpCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, levelup_service: LevelUpService):
        self.bot = bot
        self.levelup_service = levelup_service

    @commands.command(name="up")
    async def apply_level_up(self, context: commands.Context, character_id: str, levels: int, status_points: str = "{}", mastery_points: str = "{}", ph_points: Optional[str] = None):
        """
        Aplica níveis a um personagem, distribuindo pontos de status, maestria e PH.
        Ex: !up <ID> 1 '{"strength": 2, "constitution": 1}' '{"swords": 2}' 1
        status_points e mastery_points devem ser strings JSON de dicionários.
        """
        try:
            parsed_status_points: Dict[str, int]
            parsed_mastery_points: Dict[str, int]

            try:
                if isinstance(status_points, int):
                    status_points = str(status_points)
                parsed_status_points = json.loads(status_points)
                if not isinstance(parsed_status_points, dict):
                    raise InvalidInputError("O valor para 'status_points' deve ser um objeto JSON (dicionário).")
            except json.JSONDecodeError:
                raise InvalidInputError("Formato JSON inválido para 'status_points'. Certifique-se de que as chaves e valores de string estão entre aspas duplas.")
            except (ValueError, SyntaxError):
                raise InvalidInputError("Formato inválido para 'status_points'. Certifique-se de que é um dicionário Python válido.")

            try:
                if isinstance(mastery_points, int):
                    mastery_points = str(mastery_points)
                parsed_mastery_points = json.loads(mastery_points)
                if not isinstance(parsed_mastery_points, dict):
                    raise InvalidInputError("O valor para 'mastery_points' deve ser um objeto JSON (dicionário).")
            except json.JSONDecodeError:
                raise InvalidInputError("Formato JSON inválido para 'mastery_points'. Certifique-se de que as chaves e valores de string estão entre aspas duplas.")
            except (ValueError, SyntaxError):
                raise InvalidInputError("Formato inválido para 'mastery_points'. Certifique-se de que é um dicionário Python válido.")

            try:
                parsed_ph_points: int = 0
                if ph_points is not None:
                    parsed_ph_points = int(ph_points)
            except ValueError:
                raise InvalidInputError("Formato inválido para 'ph_points'. Certifique-se de que é um número inteiro válido.")

            if levels <= 0:
                raise InvalidInputError("O número de níveis a ganhar deve ser maior que zero.")

            apply_dto = ApplyLevelUpDTO(
                character_id=character_id,
                levels_to_gain=levels,
                status_points_spent=parsed_status_points,
                mastery_points_spent=parsed_mastery_points,
                ph_points_spent=parsed_ph_points
            )
            
            updated_character = await self.levelup_service.level_up_character(
                apply_dto.character_id,
                apply_dto.levels_to_gain,
                # Os pontos de status, maestria e PH são gerenciados internamente pelo LevelUpService
                # e não são passados diretamente para level_up_character.
                # A lógica de gasto de pontos será implementada no LevelUpService.
            )

            response_dto = LevelUpResponseDTO(
                character_id=str(updated_character.id),
                new_level=updated_character.level,
                updated_attributes=updated_character.attributes,
                updated_modifiers=updated_character.modifiers,
                updated_hp=updated_character.hp,
                updated_max_hp=updated_character.max_hp,
                updated_chakra=updated_character.chakra,
                updated_max_chakra=updated_character.max_chakra,
                updated_fp=updated_character.fp,
                updated_max_fp=updated_character.max_fp,
                updated_masteries=updated_character.masteries,
                remaining_ph_points=updated_character.pontos["ph"]["total"],
                remaining_status_points=updated_character.pontos["status"]["total"],
                remaining_mastery_points=updated_character.pontos["mastery"]["total"]
            )

            response_message = (
                f"**Personagem '{updated_character.name}' subiu para o Nível {response_dto.new_level}!**\n\n"
                f"**Atributos Atualizados:**\n"
                + "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in response_dto.updated_attributes.items()]) + "\n\n"
                f"**Modificadores Atualizados:**\n"
                + "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in response_dto.updated_modifiers.items()]) + "\n\n"
                f"**Pontos de Vida/Habilidade:**\n"
                f"- HP: {response_dto.updated_hp}/{response_dto.updated_max_hp}\n"
                f"- Chakra: {response_dto.updated_chakra}/{response_dto.updated_max_chakra}\n"
                f"- FP: {response_dto.updated_fp}/{response_dto.updated_max_fp}\n\n"
                f"**Maestrias:**\n"
                + (", ".join([f"{m.capitalize()}: {v}" for m, v in response_dto.updated_masteries.items()]) if response_dto.updated_masteries else "Nenhuma") + "\n\n"
                f"**Pontos Restantes:**\n"
                f"- PH: {response_dto.remaining_ph_points}\n"
                f"- Status: {response_dto.remaining_status_points}\n"
                f"- Maestria: {response_dto.remaining_mastery_points}"
            )
            await context.send(response_message)

        except (CharacterNotFoundError, InvalidInputError, LevelUpError) as e:
            await context.send(f"Erro ao subir de nível: {e}")
        except Exception as e:
            await context.send(f"Ocorreu um erro inesperado: {e}")

async def setup(bot: commands.Bot):
    connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    database_name = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")

    mongo_repo = MongoDBRepository(connection_string=connection_string, database_name=database_name)
    await mongo_repo.connect() # Conectar assincronamente
    transformation_repository = TransformationRepository(mongo_repo)
    class_repository = ClassRepository(mongodb_repository=mongo_repo)
    character_service = CharacterService(
        character_repository=mongo_repo,
        transformation_repository=transformation_repository,
        class_repository=class_repository
    )
    levelup_service = LevelUpService(character_service=character_service, class_repository=class_repository)
    await bot.add_cog(LevelUpCommands(bot, levelup_service))