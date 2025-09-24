import json
import asyncio
import os
from discord.ext import commands
from typing import Optional, Any
from dataclasses import asdict # Import asdict for dataclass serialization
import shlex
from src.core.services.character_service import CharacterService
from src.core.services.levelup_service import LevelUpService
from src.infrastructure.database.player_preferences_repository import PlayerPreferencesRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.infrastructure.database.class_repository import ClassRepository
from src.core.entities.player_preferences import PlayerPreferences
from src.application.dtos.character_dto import CreateCharacterDTO, UpdateCharacterDTO, CharacterResponseDTO
from src.utils.exceptions.application_exceptions import CharacterNotFoundError, InvalidInputError, CharacterError, PlayerPreferencesError, LevelUpError
from src.infrastructure.database.mongodb_repository import MongoDBRepository # For instantiation
from src.utils.helpers.character_parser import parse_character_sheet
from discord import Embed, Color
from src.utils.logging.logger import get_logger # Import the logger

logger = get_logger(__name__) # Initialize logger

class CharacterCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, character_service: CharacterService, levelup_service: LevelUpService, player_preferences_repository: PlayerPreferencesRepository):
        self.bot = bot
        self.character_service = character_service
        self.levelup_service = levelup_service
        self.player_preferences_repository = player_preferences_repository

    @commands.group(name="ficha", invoke_without_command=True)
    async def ficha(self, ctx: commands.Context):
        """Comandos para gerenciar fichas de personagens."""
        if ctx.invoked_subcommand is None:
            # Updated help message
            await ctx.send("Use `!ficha criar`, `!ficha ver`, `!ficha atualizar`, `!ficha excluir` ou `!ficha levelup`.")

    @ficha.command(name="criar")
    async def create_character(self, ctx: commands.Context, name: str, class_name: str, *, args: str = ""):
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
            character = await self.character_service.create_character(
                name=create_dto.name,
                player_discord_id=str(ctx.author.id),
                class_name=create_dto.class_name,
            )
            embed = Embed(
                title=f"Personagem '{character.name}' criado!",
                description=f"Classe: {character.class_name}\nNível: {character.level}\nID: `{character.id}`",
                color=Color.green()
            )
            await ctx.send(embed=embed)
        except InvalidInputError as e:
            await ctx.send(f"Erro de validação: {e}")
        except CharacterError as e:
            await ctx.send(f"Erro ao criar personagem: {e}")
        except Exception as e:
            await ctx.send(f"Ocorreu um erro inesperado: {e}")

    @ficha.command(name="ver")
    async def view_character(self, ctx, name: str):
        try:
            character = await self.character_service.get_character_with_effective_stats(name)
            
            if not character:
                await ctx.send(f"Personagem '{name}' não encontrado.")
                return

            if str(character.player_discord_id) != str(ctx.author.id):
                await ctx.send("Você não tem permissão para ver a ficha deste personagem.")
                return

            embed = Embed(
                title=f"Ficha de Personagem: {character.name}",
                description=f"ID: `{character.id}`\nAlias: {character.alias if character.alias else 'Nenhum'}",
                color=Color.blue()
            )
            embed.add_field(name="Informações Básicas", value=(
                f"Classe: {character.class_name}\n"
                f"Nível: {character.level} | XP: {character.experience}"
            ), inline=False)
            
            attributes_str = "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in character.attributes.items()])
            embed.add_field(name="Atributos Efetivos", value=attributes_str, inline=True)

            modifiers_str = "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in character.modifiers.items()])
            embed.add_field(name="Modificadores", value=modifiers_str, inline=True)

            embed.add_field(name="Recursos", value=(
                f"HP: {character.hp}/{character.max_hp}\n"
                f"Chakra: {character.chakra}/{character.max_chakra}\n"
                f"FP: {character.fp}/{character.max_fp}"
            ), inline=False)

            masteries_str = ", ".join([f"{m.capitalize()}: {v}" for m, v in character.masteries.items()]) if character.masteries else "Nenhuma"
            embed.add_field(name="Maestrias", value=masteries_str, inline=False)

            points_str = (
                f"PH: {character.pontos['ph']['total']}\n"
                f"Status: {character.pontos['status']['total']}\n"
                f"Maestria: {character.pontos['mastery']['total']}"
            )
            embed.add_field(name="Pontos Disponíveis", value=points_str, inline=False)
            
            embed.set_footer(text=f"Última Atualização: {character.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
        except CharacterNotFoundError as e:
            await ctx.send(f"Erro: {e}")
        except Exception as e:
            await ctx.send(f"Ocorreu um erro inesperado: {e}")

    @ficha.command(name="atualizar")
    async def update_character_command(self, ctx: commands.Context, identifier: str, field_name: str, *, value: str):
        """
        Atualiza um campo específico da ficha de um personagem.
        Campos permitidos: name, alias, masteries (formato JSON).
        Ex: !ficha atualizar <ID> name "Novo Nome"
        Ex: !ficha atualizar <ID> masteries '{"swords": 3, "archery": 1}'
        """
        try:
            character = await self.character_service.get_character(identifier)
            # Allow updating player_discord_id even if not owner, to claim character
            if str(character.player_discord_id) != str(ctx.author.id) and field_name != "player_discord_id":
                await ctx.send("Você não tem permissão para atualizar a ficha deste personagem.")
                return

            # Special handling for masteries if it's a JSON string
            parsed_value: Any = value
            if field_name == "masteries":
                try:
                    # Strip potential code block formatting
                    clean_value = value.strip("`'\" ")
                    parsed_value = json.loads(clean_value)
                    if not isinstance(parsed_value, dict):
                        raise InvalidInputError("O valor para 'masteries' deve ser um objeto JSON (dicionário).")
                except json.JSONDecodeError:
                    raise InvalidInputError("Formato JSON inválido para 'masteries'. Use aspas duplas para chaves e strings: `{\"swords\": 1}`")
            elif field_name == "player_discord_id":
                # Validate if the new player_discord_id is a valid Discord ID (numeric string)
                if not value.isdigit():
                    raise InvalidInputError("O player_discord_id deve ser um ID numérico válido do Discord.")
                parsed_value = value
            
            updated_character = await self.character_service.update_character(
                str(character.id), field_name, parsed_value
            )
            embed = Embed(
                title=f"Personagem '{updated_character.name}' atualizado!",
                description=f"Campo '{field_name}' atualizado com sucesso.",
                color=Color.green()
            )
            await ctx.send(embed=embed)
        except (CharacterNotFoundError, InvalidInputError, CharacterError) as e:
            await ctx.send(f"Erro ao atualizar personagem: {e}")
        except Exception as e:
            await ctx.send(f"Ocorreu um erro inesperado: {e}")

    @ficha.command(name="excluir")
    async def delete_character_command(self, ctx: commands.Context, identifier: str):
        """
        Exclui uma ficha de personagem. Requer confirmação.
        Ex: !ficha excluir <ID_DO_PERSONAGEM>
        """
        try:
            character = await self.character_service.get_character(identifier)
            if str(character.player_discord_id) != str(ctx.author.id):
                await ctx.send("Você não tem permissão para excluir a ficha deste personagem.")
                return

            await ctx.send(f"Tem certeza que deseja excluir o personagem '{character.name}' (ID: `{character.id}`)? Responda `sim` para confirmar.")
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'sim'

            try:
                confirmation = await self.bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send("Tempo esgotado. Exclusão cancelada.")
                return

            if await self.character_service.delete_character(str(character.id)):
                embed = Embed(
                    title=f"Personagem '{character.name}' excluído!",
                    description=f"ID: `{character.id}`",
                    color=Color.red()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Não foi possível excluir o personagem '{character.name}' (ID: `{character.id}`).")
        except CharacterNotFoundError as e:
            await ctx.send(f"Erro: {e}")
        except Exception as e:
            await ctx.send(f"Ocorreu um erro inesperado: {e}")

    @ficha.command(name="levelup")
    async def level_up_character_subcommand(self, ctx: commands.Context, identifier: str, levels: int = 1):
        """
        Sobe o personagem de nível.
        Ex: !ficha levelup "Meu Herói" 5
        """
        try:
            # First, get the character object
            character = await self.character_service.get_character(identifier)
            if str(character.player_discord_id) != str(ctx.author.id):
                await ctx.send("Você não tem permissão para upar este personagem.")
                return
            
            # CORRECTED: Pass the character OBJECT directly to the service
            updated_character = await self.levelup_service.level_up_character(character, levels)
            
            embed = Embed(
                title=f"Personagem '{updated_character.name}' subiu de nível!",
                description=f"Novo Nível: {updated_character.level}",
                color=Color.gold()
            )
            await ctx.send(embed=embed)
        except CharacterNotFoundError as e:
            await ctx.send(f"Erro: {e}")
        except LevelUpError as e:
            await ctx.send(f"Erro ao subir de nível: {e}")
        except Exception as e:
            await ctx.send(f"Ocorreu um erro inesperado: {e}")

    @commands.command(name="import_ficha")
    async def import_character_sheet(self, ctx: commands.Context, *, sheet_text: str):
        """
        Importa uma ficha de personagem a partir de um texto formatado.
        Ex: !import_ficha Nome: Meu Herói Nível: 1 Classe: Guerreiro For: 15 ...
        """
        try:
            character = await self.character_service.import_character(sheet_text, str(ctx.author.id))
            embed = Embed(
                title=f"Personagem '{character.name}' importado!",
                description=f"Classe: {character.class_name}\nNível: {character.level}\nID: `{character.id}`",
                color=Color.green()
            )
            await ctx.send(embed=embed)
        except InvalidInputError as e:
            await ctx.send(f"Erro de validação na importação: {e}")
        except CharacterError as e:
            await ctx.send(f"Erro ao importar personagem: {e}")
        except Exception as e:
            await ctx.send(f"Ocorreu um erro inesperado: {e}")

    @commands.command(name="favorito")
    async def set_favorite_character(self, ctx: commands.Context, identifier: str):
        """
        Define um personagem como favorito.
        Ex: !favorito "Meu Herói"
        """
        try:
            character = await self.character_service.get_character(identifier)
            if str(character.player_discord_id) != str(ctx.author.id):
                await ctx.send("Você não tem permissão para definir este personagem como favorito.")
                return

            logger.info(f"[{ctx.author.id}] Tentando obter preferências do jogador.")
            preferences = await self.player_preferences_repository.get_preferences(str(ctx.author.id))
            if not preferences:
                logger.info(f"[{ctx.author.id}] Preferências não encontradas, criando novas.")
                preferences = PlayerPreferences(player_discord_id=str(ctx.author.id))
            
            preferences.favorite_character_id = str(character.id)
            logger.info(f"[{ctx.author.id}] Definindo personagem favorito para ID: {character.id}. Salvando preferências.")
            await self.player_preferences_repository.save_preferences(preferences)
            logger.info(f"[{ctx.author.id}] Preferências salvas com sucesso para o personagem ID: {character.id}.")

            embed = Embed(
                title=f"Personagem '{character.name}' definido como favorito!",
                description=f"Agora, '{character.name}' é o seu personagem favorito.",
                color=Color.purple()
            )
            await ctx.send(embed=embed)
        except CharacterNotFoundError as e:
            logger.error(f"[{ctx.author.id}] Erro ao definir favorito (Personagem não encontrado): {e}")
            await ctx.send(f"Erro: {e}")
        except PlayerPreferencesError as e:
            logger.error(f"[{ctx.author.id}] Erro ao definir favorito (Preferências do jogador): {e}")
            await ctx.send(f"Erro ao definir favorito: {e}")
        except Exception as e:
            logger.critical(f"[{ctx.author.id}] Ocorreu um erro inesperado ao definir favorito: {e}", exc_info=True)
            await ctx.send(f"Ocorreu um erro inesperado: {e}")

    @ficha.command(name="limpar", help="Limpa todos os personagens do banco de dados (apenas para administradores).")
    @commands.has_permissions(administrator=True)
    async def clear_all_characters(self, ctx):
        try:
            deleted_count = await self.character_service.delete_all_characters()
            await ctx.send(f"Foram deletados {deleted_count} personagens do banco de dados.")
        except Exception as e:
            await ctx.send(f"Erro ao limpar personagens: {e}")

async def setup(bot: commands.Bot):
    connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    database_name = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")

    # Instanciar o MongoDBRepository e conectar
    mongodb_repo = MongoDBRepository(
        connection_string=connection_string,
        database_name=database_name
    )
    await mongodb_repo.connect() # Conectar assincronamente

    # Passar a instância conectada para os repositórios específicos
    character_repo = mongodb_repo
    transformation_repo = TransformationRepository(mongodb_repo)
    class_repo = ClassRepository(mongodb_repo)
    player_preferences_repo = PlayerPreferencesRepository(mongodb_repository=mongodb_repo)

    character_service = CharacterService(
        character_repository=character_repo,
        transformation_repository=transformation_repo,
        class_repository=class_repo
    )
    levelup_service = LevelUpService(
        character_service=character_service,
        class_repository=class_repo
    )
    
    await bot.add_cog(CharacterCommands(bot, character_service, levelup_service, player_preferences_repo))

