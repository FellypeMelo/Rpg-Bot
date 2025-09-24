from discord.ext import commands
from discord import Message
from typing import Optional, Dict, Any

# Import necessary entities, services, and repositories
from src.core.entities.character import Character
from src.core.entities.class_template import ClassTemplate
from src.core.services.character_service import CharacterService
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.infrastructure.database.class_repository import ClassRepository
from src.utils.exceptions.application_exceptions import CharacterNotFoundError, InvalidInputError

# --- Configuration ---
import os
from discord.ext import commands
from discord import Message
from typing import Optional, Dict, Any

# Import necessary entities, services, and repositories
from src.core.entities.character import Character
from src.core.entities.class_template import ClassTemplate
from src.core.services.character_service import CharacterService
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.infrastructure.database.class_repository import ClassRepository
from src.utils.exceptions.application_exceptions import CharacterNotFoundError, InvalidInputError

class ClassCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, character_service: CharacterService, class_repository: ClassRepository):
        self.bot = bot
        self.character_service = character_service
        self.class_repository = class_repository

    @commands.command(name='multiclasse')
    async def multiclasse(self, ctx: commands.Context, character_name: str, class_name: str):
        """
        Permite que um personagem adote uma segunda classe.
        Uso: !multiclasse "NomePersonagem" "NomeClasse"
        """
        try:
            # 1. Validar se o personagem existe.
            character: Character = await self.character_service.get_character(character_name)

            # 2. Validar se o dono do personagem é quem executa o comando.
            if character.player_discord_id != str(ctx.author.id):
                await ctx.send("Você não tem permissão para modificar este personagem.")
                return

            # 3. Validar se a classe é válida.
            class_template: Optional[ClassTemplate] = await self.class_repository.get_class_by_name(class_name)
            if not class_template:
                raise InvalidInputError(f"A classe '{class_name}' é inválida.")

            # 4. Adicionar o ID da nova classe à lista classe_ids do personagem e persistir.
            await self.character_service.add_multiclass(str(character.id), class_name)

            # 5. Informar o jogador sobre a adição da nova classe e como isso afetará os cálculos futuros.
            await ctx.send(
                f"Parabéns! {character_name} agora também é um(a) {class_name}.\n"
                f"Esta nova classe trará novas habilidades e desafios. "
                f"Seus atributos e perícias serão recalculados para refletir esta mudança."
            )

        except CharacterNotFoundError:
            await ctx.send(f"Personagem '{character_name}' não encontrado.")
        except InvalidInputError as e:
            await ctx.send(str(e))
        except Exception as e:
            print(f"An unexpected error occurred in multiclasse command: {e}")
            await ctx.send("Ocorreu um erro inesperado ao tentar adicionar a nova classe.")

async def setup(bot: commands.Bot):
    mongo_connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    mongo_database_name = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")

    # Repositórios
    mongodb_repo = MongoDBRepository(
        connection_string=mongo_connection_string,
        database_name=mongo_database_name
    )
    await mongodb_repo.connect() # Conectar assincronamente
    transformation_repo = TransformationRepository(mongodb_repo)
    class_repo = ClassRepository(mongodb_repo)

    # Serviços
    character_service = CharacterService(
        character_repository=mongodb_repo,
        transformation_repository=transformation_repo,
        class_repository=class_repo
    )

    await bot.add_cog(ClassCommands(bot, character_service, class_repo))
