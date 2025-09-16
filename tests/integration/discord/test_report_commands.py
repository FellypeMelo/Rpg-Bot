import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from discord.ext import commands
from src.application.commands.report_commands import ReportCommands
from src.core.services.report_service import ReportService
from src.core.entities.character import Character
from src.utils.exceptions.application_exceptions import CharacterNotFoundError

class TestReportCommands(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_bot = AsyncMock(spec=commands.Bot)
        self.mock_report_service = MagicMock(spec=ReportService)
        self.report_commands = ReportCommands(self.mock_bot, self.mock_report_service)

        self.mock_context = AsyncMock(spec=commands.Context)
        self.mock_context.send = AsyncMock()
        self.mock_context.author = MagicMock(id="player123")
        self.mock_context.guild = MagicMock(id="guild456")
        self.mock_context.channel = MagicMock(id="channel789")
        self.mock_context.command = MagicMock(name="progresso")
        # self.mock_context.bot = self.mock_bot # Removido, pois não é necessário para a nova abordagem de mock

        self.mock_character = Character(
            name="TestChar",
            class_name="Warrior",
            attributes={"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
            hp=100, max_hp=100, chakra=50, max_chakra=50, fp=30, max_fp=30,
            level=5, experience=1200, ph_points=3, status_points=2, mastery_points=1, masteries={"swords": 2}
        )
        self.mock_character.id = "test_char_id"
        self.mock_character.calculate_modifiers()

        self.mock_report = {
            "character_name": "TestChar",
            "level": 5,
            "experience": 1200,
            "attributes": {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
            "modifiers": {"strength": 2, "dexterity": 2, "constitution": 2, "intelligence": 2, "wisdom": 2, "charisma": 2},
            "hp": "100/100",
            "chakra": "50/50",
            "fp": "30/30",
            "masteries": {"swords": 2},
            "ph_points": 3,
            "status_points_available": 2,
            "mastery_points_available": 1,
            "last_updated": self.mock_character.updated_at
        }

    async def test_progress_report_success(self):
        self.mock_report_service.get_progress_report.return_value = self.mock_report

        await self.report_commands.progress_report.callback(
            self.report_commands, self.mock_context, self.mock_character.id
        )
        # mock_progress_report.assert_called_once_with(self.mock_context, self.mock_character.id) # Removido

        self.mock_report_service.get_progress_report.assert_called_once_with(self.mock_character.id)
        self.mock_context.send.assert_called_once()
        self.assertIn("Relatório de Progresso: TestChar", self.mock_context.send.call_args[0][0])
        self.assertIn("Nível: 5", self.mock_context.send.call_args[0][0])

    async def test_progress_report_character_not_found(self):
        self.mock_report_service.get_progress_report.side_effect = CharacterNotFoundError("Personagem não encontrado.")

        await self.report_commands.progress_report.callback(
            self.report_commands, self.mock_context, "non_existent_id"
        )
        # mock_progress_report.assert_called_once_with(self.mock_context, "non_existent_id") # Removido

        self.mock_context.send.assert_called_once_with("Erro ao gerar relatório de progresso: Personagem não encontrado.")

    async def test_usage_statistics_success(self):
        mock_stats = {
            "total_characters": 2,
            "class_distribution": {"Warrior": 1, "Mage": 1},
            "average_character_level": 4.0
        }
        self.mock_report_service.get_usage_statistics.return_value = mock_stats

        await self.report_commands.usage_statistics.callback(
            self.report_commands, self.mock_context
        )
        # mock_usage_statistics.assert_called_once_with(self.mock_context) # Removido

        self.mock_report_service.get_usage_statistics.assert_called_once()
        self.mock_context.send.assert_called_once()
        self.assertIn("Estatísticas de Uso do RPG Bot", self.mock_context.send.call_args[0][0])
        self.assertIn("Total de Personagens Registrados: 2", self.mock_context.send.call_args[0][0])
        self.assertIn("Nível Médio dos Personagens: 4.0", self.mock_context.send.call_args[0][0])
        self.assertIn("- Warrior: 1", self.mock_context.send.call_args[0][0])
        self.assertIn("- Mage: 1", self.mock_context.send.call_args[0][0])

    async def test_usage_statistics_error(self):
        self.mock_report_service.get_usage_statistics.side_effect = Exception("Erro ao buscar estatísticas.")

        await self.report_commands.usage_statistics.callback(
            self.report_commands, self.mock_context
        )
        # mock_usage_statistics.assert_called_once_with(self.mock_context) # Removido

        self.mock_context.send.assert_called_once_with("Erro ao gerar estatísticas de uso: Erro ao buscar estatísticas.")

if __name__ == '__main__':
    unittest.main()