import json
import asyncio
import os
from discord.ext import commands
from typing import Optional, Any
from dataclasses import asdict # Import asdict for dataclass serialization
import shlex
from src.core.services.character_service import CharacterService
from src.application.dtos.character_dto import CreateCharacterDTO, UpdateCharacterDTO, CharacterResponseDTO
from src.utils.exceptions.application_exceptions import CharacterNotFoundError, InvalidInputError, CharacterError
from src.infrastructure.database.mongodb_repository import MongoDBRepository # For instantiation

class CharacterCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, character_service: CharacterService):
        self.bot = bot
        self.character_service = character_service

    @commands.group(name="ficha", invoke_without_command=True)
    async def ficha(self, context: commands.Context):
        """Comandos para gerenciar fichas de personagens."""
        if context.invoked_subcommand is None:
            await context.send("Use `!ficha criar`, `!ficha ver`, `!ficha atualizar` ou `!ficha excluir`.")

    @ficha.command(name="criar")
    async def create_character(self, context: commands.Context, name: str, class_name: str, *, args: str = ""):
        """
        Cria uma nova ficha de personagem.
        Ex: !ficha criar "Meu Herói" Guerreiro --alias "O Bravo"
        """
        try:
            parsed_args = shlex.split(args)
            alias = None

            # Basic parsing for --alias flag
            if "--alias" in parsed_args:
                alias_index = parsed_args.index("--alias")
                if alias_index + 1 < len(parsed_args):
                    alias = parsed_args[alias_index + 1]

            create_dto = CreateCharacterDTO(name=name, class_name=class_name, alias=alias)
            character = self.character_service.create_character(
                name=create_dto.name,
                class_name=create_dto.class_name,
                alias=create_dto.alias,
                base_attributes=None # Explicitly set to None since not implemented in command yet
            )
            response_dto = CharacterResponseDTO(
                id=character.id,
                name=character.name,
                alias=character.alias,
                class_name=character.class_name,
                level=character.level,
                experience=character.experience,
                attributes=character.attributes,
                modifiers=character.modifiers,
                hp=character.hp,
                max_hp=character.max_hp,
                chakra=character.chakra,
                max_chakra=character.max_chakra,
                fp=character.fp,
                max_fp=character.max_fp,
                masteries=character.masteries,
                ph_points=character.ph_points,
                status_points=character.status_points,
                mastery_points=character.mastery_points,
                inventory=character.inventory,
                skills=character.skills,
                spells=character.spells,
                equipment=character.equipment,
                created_at=character.created_at,
                updated_at=character.updated_at,
            )
            await context.send(f"Personagem '{response_dto.name}' da classe '{response_dto.class_name}' criado com sucesso! ID: `{response_dto.id}`")
            # Optionally, send a formatted character sheet
            await context.send(f"```json\n{json.dumps(asdict(response_dto), indent=2)}\n```")
        except InvalidInputError as e:
            await context.send(f"Erro de validação: {e}")
        except CharacterError as e:
            await context.send(f"Erro ao criar personagem: {e}")
        except Exception as e:
            await context.send(f"Ocorreu um erro inesperado: {e}")

    @ficha.command(name="ver")
    async def view_character(self, context: commands.Context, identifier: str):
        """
        Exibe a ficha completa de um personagem.
        Ex: !ficha ver <ID_DO_PERSONAGEM> ou !ficha ver "Nome do Personagem"
        """
        try:
            character = self.character_service.get_character(identifier)
            response_dto = CharacterResponseDTO(
                id=character.id,
                name=character.name,
                alias=character.alias,
                class_name=character.class_name,
                level=character.level,
                experience=character.experience,
                attributes=character.attributes,
                modifiers=character.modifiers,
                hp=character.hp,
                max_hp=character.max_hp,
                chakra=character.chakra,
                max_chakra=character.max_chakra,
                fp=character.fp,
                max_fp=character.max_fp,
                masteries=character.masteries,
                ph_points=character.ph_points,
                status_points=character.status_points,
                mastery_points=character.mastery_points,
                inventory=character.inventory,
                skills=character.skills,
                spells=character.spells,
                equipment=character.equipment,
                created_at=character.created_at,
                updated_at=character.updated_at,
            )
            # Format the output nicely
            response_message = (
                f"**Ficha de Personagem: {response_dto.name}** (ID: `{response_dto.id}`)\n"
                f"Alias: {response_dto.alias if response_dto.alias else 'Nenhum'}\n"
                f"Classe: {response_dto.class_name} | Nível: {response_dto.level} | XP: {response_dto.experience}\n\n"
                f"**Atributos Base:**\n"
                + "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in response_dto.attributes.items()]) + "\n\n"
                f"**Modificadores:**\n"
                + "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in response_dto.modifiers.items()]) + "\n\n"
                f"**Pontos de Vida/Habilidade:**\n"
                f"- HP: {response_dto.hp}/{response_dto.max_hp}\n"
                f"- Chakra: {response_dto.chakra}/{response_dto.max_chakra}\n"
                f"- FP: {response_dto.fp}/{response_dto.max_fp}\n\n"
                f"**Maestrias:**\n"
                + (", ".join([f"{m.capitalize()}: {v}" for m, v in response_dto.masteries.items()]) if response_dto.masteries else "Nenhuma") + "\n\n"
                f"**Pontos Disponíveis:**\n"
                f"- PH: {response_dto.ph_points}\n"
                f"- Status: {response_dto.status_points}\n"
                f"- Maestria: {response_dto.mastery_points}\n\n"
                f"Última Atualização: {response_dto.updated_at}"
            )
            await context.send(response_message)
        except CharacterNotFoundError as e:
            await context.send(f"Erro: {e}")
        except Exception as e:
            await context.send(f"Ocorreu um erro inesperado: {e}")

    @ficha.command(name="atualizar")
    async def update_character_command(self, context: commands.Context, character_id: str, field_name: str, *, value: str):
        """
        Atualiza um campo específico da ficha de um personagem.
        Campos permitidos: name, alias, masteries (formato JSON).
        Ex: !ficha atualizar <ID> name "Novo Nome"
        Ex: !ficha atualizar <ID> masteries '{"swords": 3, "archery": 1}'
        """
        try:
            # Special handling for masteries if it's a JSON string
            parsed_value: Any = value
            if field_name == "masteries":
                try:
                    parsed_value = json.loads(value)
                    if not isinstance(parsed_value, dict):
                        raise InvalidInputError("O valor para 'masteries' deve ser um objeto JSON (dicionário).")
                except json.JSONDecodeError:
                    raise InvalidInputError("Formato JSON inválido para 'masteries'.")
            
            update_dto = UpdateCharacterDTO(character_id=character_id, field_name=field_name, value=parsed_value)
            updated_character = self.character_service.update_character(
                update_dto.character_id, update_dto.field_name, update_dto.value
            )
            await context.send(f"Personagem '{updated_character.name}' (ID: `{updated_character.id}`) atualizado com sucesso!")
        except (CharacterNotFoundError, InvalidInputError, CharacterError) as e:
            await context.send(f"Erro ao atualizar personagem: {e}")
        except Exception as e:
            await context.send(f"Ocorreu um erro inesperado: {e}")

    @ficha.command(name="excluir")
    async def delete_character_command(self, context: commands.Context, character_id: str):
        """
        Exclui uma ficha de personagem. Requer confirmação.
        Ex: !ficha excluir <ID_DO_PERSONAGEM>
        """
        try:
            # Implement a simple confirmation mechanism
            await context.send(f"Tem certeza que deseja excluir o personagem com ID `{character_id}`? Responda `sim` para confirmar.")
            
            def check(m):
                return m.author == context.author and m.channel == context.channel and m.content.lower() == 'sim'

            try:
                confirmation = await self.bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await context.send("Tempo esgotado. Exclusão cancelada.")
                return

            # The delete_character method doesn't need any additional parameters
            if self.character_service.delete_character(character_id):
                await context.send(f"Personagem com ID `{character_id}` excluído com sucesso.")
            else:
                await context.send(f"Não foi possível excluir o personagem com ID `{character_id}`.")
        except CharacterNotFoundError as e:
            await context.send(f"Erro: {e}")
        except Exception as e:
            await context.send(f"Ocorreu um erro inesperado: {e}")

async def setup(bot: commands.Bot):
    # Instantiate repository and service
    # These should ideally be injected via a dependency injection framework
    # For now, we'll instantiate them directly
    mongo_repo = MongoDBRepository(
        connection_string=os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/"),
        database_name=os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db"),
        collection_name=os.getenv("MONGODB_CHARACTER_COLLECTION", "characters")
    )
    character_service = CharacterService(character_repository=mongo_repo)
    await bot.add_cog(CharacterCommands(bot, character_service))