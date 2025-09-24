import os
from discord.ext import commands
from typing import Optional

# Import necessary components
# Import necessary components and services
from src.core.calculators.attribute_roller import roll_attribute # This function will return (d20_roll, total_roll)
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.infrastructure.database.class_repository import ClassRepository
# Assuming PlayerPreferences or a similar entity/service is used to store/retrieve favorite character
from src.core.services.character_service import CharacterService
from src.infrastructure.database.player_preferences_repository import PlayerPreferencesRepository
from src.utils.logging.logger import get_logger # Import the logger

logger = get_logger(__name__) # Initialize logger

class DiceCommands(commands.Cog):
    """
    Comandos relacionados a rolagens de dados.
    """
    def __init__(self, bot: commands.Bot, character_service: CharacterService, player_preferences_repository: PlayerPreferencesRepository):
        self.bot = bot
        self.character_service = character_service
        self.player_preferences_repository = player_preferences_repository

# Removed instantiation of AttributeRoller and CharacterParser as they are now functions.
# The character_service is used to fetch the favorite character.
# The roll_attribute function will be called directly in the rodar command.

    @commands.command(name='rodar', help='Rola Xd20 + modificador de atributo + bônus. Ex: !rodar 2 Força 5 ou !rodar Força 5 (padrão 1d20). Se nenhum argumento for fornecido, rola 1d20 para Força automaticamente.')
    async def rodar(self, ctx: commands.Context, *args):
        """
        Rola Xd20 + modificador do atributo do personagem favorito do jogador.
        Soma um bônus adicional se fornecido.
        """
        num_dice = 1
        attribute = "strength"
        bonus = 0

        if not args:
            # No arguments provided, default to rolling 1d20 for 'strength'
            # num_dice and attribute are already set to default values
            pass
        elif len(args) == 1:
            # Could be attribute or num_dice
            if args[0].isdigit():
                num_dice = int(args[0])
                # If only num_dice is provided, assume strength as attribute
                attribute = "strength"
            else:
                attribute = args[0]
        elif len(args) == 2:
            # Could be num_dice and attribute, or attribute and bonus
            if args[0].isdigit():
                num_dice = int(args[0])
                attribute = args[1]
            else:
                attribute = args[0]
                if args[1].isdigit():
                    bonus = int(args[1])
                else:
                    await ctx.send("Formato inválido. Se você não especificar o número de dados, o segundo argumento deve ser o bônus. Ex: `!rodar Força 5`")
                    return
        elif len(args) == 3:
            # num_dice, attribute, bonus
            if args[0].isdigit():
                num_dice = int(args[0])
                attribute = args[1]
                if args[2].isdigit():
                    bonus = int(args[2])
                else:
                    await ctx.send("Formato inválido para o bônus. Ex: `!rodar 2 Força 5`")
                    return
            else:
                await ctx.send("Formato inválido. O primeiro argumento deve ser o número de dados se houver três argumentos. Ex: `!rodar 2 Força 5`")
                return
        else:
            await ctx.send("Número de argumentos inválido. Use `!ajuda rodar` para ver os exemplos.")
            return

        player_discord_id = str(ctx.author.id)

        # 1. Obter o personagem favorito do jogador
        logger.info(f"[{player_discord_id}] Buscando preferências para o comando !rodar.")
        preferences = await self.player_preferences_repository.get_preferences(player_discord_id)
        if not preferences or not preferences.favorite_character_id:
            logger.warning(f"[{player_discord_id}] Nenhuma preferência ou ID de personagem favorito encontrado.")
            await ctx.send("Você ainda não definiu um personagem favorito. Use `!favorito <ID_DO_PERSONAGEM>` para definir um.")
            return

        favorite_character_id = preferences.favorite_character_id
        logger.info(f"[{player_discord_id}] ID do personagem favorito encontrado: {favorite_character_id}. Buscando dados do personagem.")
        favorite_character_data = await self.character_service.get_character_with_effective_stats(favorite_character_id)

        if not favorite_character_data:
            logger.error(f"[{player_discord_id}] Personagem favorito com ID '{favorite_character_id}' não encontrado no banco de dados.")
            await ctx.send("O personagem favorito definido não foi encontrado. Por favor, defina um novo favorito com `!favorito`.")
            return

        # 2. Realizar a rolagem usando AttributeRoller
        # Assuming AttributeRoller.roll_with_modifier handles:
        # Helper function to calculate modifier from attribute value


        # Extract character data assuming it's a Character object
        # Assuming favorite_character_data is a Character object, access its attributes directly.
        # If it's a dictionary, use .get() as before.
        character_attributes = favorite_character_data.attributes
        character_name = favorite_character_data.name

        attribute_name_lower = attribute.lower()
        
        # Mapeamento de nomes curtos para nomes completos de atributos
        attribute_map = {
            "for": "strength",
            "des": "dexterity",
            "con": "constitution",
            "int": "intelligence",
            "sab": "wisdom",
            "car": "charisma",
            "strength": "strength",
            "dexterity": "dexterity",
            "constitution": "constitution",
            "intelligence": "intelligence",
            "wisdom": "wisdom",
            "charisma": "charisma",
        }

        full_attribute_name = attribute_map.get(attribute_name_lower)

        if full_attribute_name is None:
            await ctx.send(f"Atributo '{attribute}' inválido. Use um dos seguintes: Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma (ou suas abreviações: for, des, con, int, sab, car).")
            return

        attribute_value = character_attributes.get(full_attribute_name)

        if attribute_value is None:
            await ctx.send(f"O atributo '{full_attribute_name.capitalize()}' não foi encontrado no personagem '{character_name}'.")
            return
        
        modifier = favorite_character_data.modifiers.get(full_attribute_name)
        if modifier is None:
            await ctx.send(f"O modificador para '{full_attribute_name.capitalize()}' não foi encontrado no personagem '{character_name}'.")
            return

        # Perform the roll using the imported function
        try:
            # roll_attribute returns a tuple (d20_roll, total_roll)
            d20_rolls = []
            total_roll = 0
            for _ in range(num_dice):
                d20_roll, current_total_roll = roll_attribute(
                    base_attribute_value=attribute_value,
                    modifier=modifier,
                    additional_bonus=bonus if bonus is not None else 0
                )
                d20_rolls.append(str(d20_roll))
                total_roll += current_total_roll

            # 3. Formatar a resposta
            # The prompt requires clear formatting: showing the roll, modifier, bonus, and final result.
            # Assuming roll_result has attributes like:
            # - base_roll (e.g., 15)
            # - modifier (e.g., 3)
            # - bonus (the additional bonus provided, which is `bonus` parameter)
            # - total (final result)
            # - attribute_name (the attribute rolled, e.g., "Força")
            # - character_name (the name of the character used, e.g., "Guerreiro")

            # Ensure attribute name is capitalized for display
            display_attribute = attribute.capitalize()
    
            response = (
                f"**{ctx.author.display_name}** rolou para **{character_name}**:\n"
                f"**{display_attribute}** ({num_dice}d20 + Modificador + Bônus):\n"
                f"- Rolagem base: {', '.join(d20_rolls)}\n"
                f"- Modificador de {display_attribute}: {modifier}\n" # Use calculated modifier
                f"- Bônus adicional: {bonus}\n"
                f"**Resultado Final:** {total_roll}"
            )
            await ctx.send(response)
    
        except Exception as e:
            # Catch any other unexpected errors
            await ctx.send(f"Ocorreu um erro inesperado ao tentar rolar o atributo {attribute}.")
            print(f"Unexpected error in !rodar command: {e}")
    
    # This is a standard way to add a Cog to a Discord bot.
    # It assumes the bot is set up to load cogs.
async def setup(bot: commands.Bot):
    # Database connection details
    MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")

    mongo_repo = MongoDBRepository(connection_string=MONGODB_CONNECTION_STRING, database_name=MONGODB_DATABASE_NAME)
    await mongo_repo.connect() # Conectar assincronamente

    # Instantiate repositories
    transformation_repo = TransformationRepository(mongodb_repository=mongo_repo)
    class_repo = ClassRepository(mongodb_repository=mongo_repo)
    player_preferences_repo = PlayerPreferencesRepository(mongodb_repository=mongo_repo)

    # Instantiate CharacterService with dependencies
    character_service = CharacterService(
        character_repository=mongo_repo,
        transformation_repository=transformation_repo,
        class_repository=class_repo
    )
    
    # Pass all required dependencies to the Cog
    await bot.add_cog(DiceCommands(bot, character_service, player_preferences_repo))