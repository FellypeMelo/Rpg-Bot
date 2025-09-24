from discord.ext import commands
from typing import Optional
from src.core.services.report_service import ReportService
from src.core.services.character_service import CharacterService
from src.infrastructure.database.mongodb_repository import MongoDBRepository # For instantiation
from src.infrastructure.database.player_preferences_repository import PlayerPreferencesRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.infrastructure.database.class_repository import ClassRepository
import os

class ReportCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, report_service: ReportService, character_service: CharacterService, player_preferences_repository: PlayerPreferencesRepository):
        self.bot = bot
        self.report_service = report_service
        self.character_service = character_service
        self.player_preferences_repository = player_preferences_repository

    @commands.command(name="progresso")
    async def progress_report(self, context: commands.Context, character_id: Optional[str] = None):
        """
        Exibe o relatório de progresso de um personagem.
        Se nenhum ID for fornecido, tenta usar o personagem favorito do jogador.
        Ex: !progresso <ID_DO_PERSONAGEM>
        Ex: !progresso (para usar o personagem favorito)
        """
        target_character_id = character_id
        if not target_character_id:
            preferences = await self.player_preferences_repository.get_preferences(str(context.author.id))
            if preferences and preferences.favorite_character_id:
                target_character_id = preferences.favorite_character_id
            else:
                await context.send("Por favor, forneça o ID do personagem ou defina um personagem favorito com `!favorito <ID_DO_PERSONAGEM>`.")
                return

        try:
            report = await self.report_service.get_progress_report(target_character_id)
            
            response_message = (
                f"**Relatório de Progresso: {report['character_name']}** (ID: `{target_character_id}`)\n"
                f"Nível: {report['level']} | XP: {report['experience']}\n\n"
                f"**Atributos:**\n"
                + "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in report['attributes'].items()]) + "\n\n"
                f"**Modificadores:**\n"
                + "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in report['modifiers'].items()]) + "\n\n"
                f"**Pontos de Vida/Habilidade:**\n"
                f"- HP: {report['hp']}\n"
                f"- Chakra: {report['chakra']}\n"
                f"- FP: {report['fp']}\n\n"
                f"**Maestrias:**\n"
                + (", ".join([f"{m.capitalize()}: {v}" for m, v in report['masteries'].items()]) if report['masteries'] else "Nenhuma") + "\n\n"
                f"**Pontos Disponíveis:**\n"
                f"- PH: {report['ph_points']}\n"
                f"- Status: {report['status_points_available']}\n"
                f"- Maestria: {report['mastery_points_available']}\n\n"
                f"Última Atualização: {report['last_updated']}"
            )
            await context.send(response_message)
        except Exception as e:
            await context.send(f"Erro ao gerar relatório de progresso: {e}")

    @commands.command(name="stats")
    async def usage_statistics(self, context: commands.Context):
        """
        Exibe estatísticas de uso do bot.
        Ex: !stats
        """
        try:
            stats = await self.report_service.get_usage_statistics()
            
            class_distribution_str = "\n".join([f"- {cls}: {count}" for cls, count in stats['class_distribution'].items()]) if stats['class_distribution'] else "Nenhuma classe registrada."

            response_message = (
                f"**Estatísticas de Uso do RPG Bot**\n\n"
                f"Total de Personagens Registrados: {stats['total_characters']}\n"
                f"Nível Médio dos Personagens: {stats['average_character_level']}\n\n"
                f"**Distribuição de Classes:**\n"
                f"{class_distribution_str}\n\n"
                f"*(Mais estatísticas em breve!)*"
            )
            await context.send(response_message)
        except Exception as e:
            await context.send(f"Erro ao gerar estatísticas de uso: {e}")

async def setup(bot: commands.Bot):
    connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    database_name = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")

    mongodb_repo = MongoDBRepository(
        connection_string=connection_string,
        database_name=database_name
    )
    await mongodb_repo.connect()

    character_repo = mongodb_repo
    transformation_repo = TransformationRepository(mongodb_repo)
    class_repo = ClassRepository(mongodb_repo)
    player_preferences_repo = PlayerPreferencesRepository(mongodb_repository=mongodb_repo)

    character_service = CharacterService(
        character_repository=character_repo,
        transformation_repository=transformation_repo,
        class_repository=class_repo
    )
    report_service = ReportService(character_repository=mongodb_repo)
    await bot.add_cog(ReportCommands(bot, report_service, character_service, player_preferences_repo))