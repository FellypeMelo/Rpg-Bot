from discord.ext import commands
from typing import Optional
from src.core.services.report_service import ReportService
from src.infrastructure.database.mongodb_repository import MongoDBRepository # For instantiation
import os

class ReportCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, report_service: ReportService):
        self.bot = bot
        self.report_service = report_service

    @commands.command(name="progresso")
    async def progress_report(self, context: commands.Context, character_id: str):
        """
        Exibe o relatório de progresso de um personagem.
        Ex: !progresso <ID_DO_PERSONAGEM>
        """
        try:
            report = self.report_service.get_progress_report(character_id)
            
            response_message = (
                f"**Relatório de Progresso: {report['character_name']}** (ID: `{character_id}`)\n"
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
            stats = self.report_service.get_usage_statistics()
            
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
    mongo_repo = MongoDBRepository(
        connection_string=os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/"),
        database_name=os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db"),
        collection_name=os.getenv("MONGODB_CHARACTER_COLLECTION", "characters")
    )
    report_service = ReportService(character_repository=mongo_repo)
    await bot.add_cog(ReportCommands(bot, report_service))