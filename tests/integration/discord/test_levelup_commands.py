import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from discord.ext import commands
from src.application.commands.levelup_commands import LevelUpCommands
from src.core.services.levelup_service import LevelUpService
from src.core.entities.character import Character
from src.utils.exceptions.application_exceptions import LevelUpError, InvalidInputError, CharacterNotFoundError

class TestLevelUpCommands(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_bot = AsyncMock(spec=commands.Bot)
        self.mock_levelup_service = MagicMock(spec=LevelUpService)
        self.levelup_commands = LevelUpCommands(self.mock_bot, self.mock_levelup_service)

        self.mock_context = AsyncMock(spec=commands.Context)
        self.mock_context.send = AsyncMock()
        self.mock_context.author = MagicMock(id="player123")
        self.mock_context.guild = MagicMock(id="guild456")
        self.mock_context.channel = MagicMock(id="channel789")
        self.mock_context.command = MagicMock(name="up")
        # self.mock_context.bot = self.mock_bot # Removido, pois não é necessário para a nova abordagem de mock

        self.mock_character = Character(
            name="TestChar",
            class_name="Warrior",
            attributes={"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
            hp=100, max_hp=100, chakra=50, max_chakra=50, fp=30, max_fp=30,
            level=1, experience=0, ph_points=0, status_points=0, mastery_points=0, masteries={}
        )
        self.mock_character.id = "test_char_id"

    async def test_apply_level_up_success(self):
        self.mock_levelup_service.apply_level_up.return_value = self.mock_character
        self.mock_character.level = 2 # Simulate level up
        self.mock_character.attributes["strength"] = 12 # Simulate attribute increase

        await self.levelup_commands.apply_level_up.callback(
            self.levelup_commands, self.mock_context, "test_char_id", 1, '{"strength": 2}', '{"swords": 1}', 1
        )
        # As asserções para mock_apply_level_up foram removidas

        self.mock_levelup_service.apply_level_up.assert_called_once_with(
            "test_char_id", 1, {"strength": 2}, {"swords": 1}, 1
        )
        self.mock_context.send.assert_called_once()
        self.assertIn("subiu para o Nível 2!", self.mock_context.send.call_args[0][0])
        self.assertIn("Strength: 12", self.mock_context.send.call_args[0][0])

    async def test_apply_level_up_character_not_found(self):
        self.mock_levelup_service.apply_level_up.side_effect = CharacterNotFoundError("Personagem não encontrado.")

        await self.levelup_commands.apply_level_up.callback(
            self.levelup_commands, self.mock_context, "non_existent_id", 1, "{}", "{}", 0
        )

        self.mock_context.send.assert_called_once_with("Erro ao subir de nível: Personagem não encontrado.")

    async def test_apply_level_up_invalid_input_error(self):
        self.mock_levelup_service.apply_level_up.side_effect = InvalidInputError("O número de níveis a ganhar deve ser maior que zero.")

        await self.levelup_commands.apply_level_up.callback(
            self.levelup_commands, self.mock_context, "test_char_id", 0, "{}", "{}", 0
        )
        # mock_apply_level_up.assert_called_once_with(self.mock_context, "test_char_id", 0, "{}", "{}", 0) # Removido

        self.mock_context.send.assert_called_once_with("Erro ao subir de nível: O número de níveis a ganhar deve ser maior que zero.")

    async def test_apply_level_up_invalid_json_status_points(self):
        await self.levelup_commands.apply_level_up.callback(
            self.levelup_commands, self.mock_context, "test_char_id", 1, "invalid_json", "{}", 0
        )
        self.mock_context.send.assert_called_once_with("Erro ao subir de nível: Formato JSON inválido para 'status_points'.")

    async def test_apply_level_up_invalid_json_mastery_points(self):
        await self.levelup_commands.apply_level_up.callback(
            self.levelup_commands, self.mock_context, "test_char_id", 1, "{}", "invalid_json", 0
        )
        self.mock_context.send.assert_called_once_with("Erro ao subir de nível: Formato JSON inválido para 'mastery_points'.")

    async def test_apply_level_up_levelup_error(self):
        self.mock_levelup_service.apply_level_up.side_effect = LevelUpError("Erro de lógica de nível.")

        await self.levelup_commands.apply_level_up.callback(
            self.levelup_commands, self.mock_context, "test_char_id", 1, "{}", "{}", 0
        )
        # mock_apply_level_up.assert_called_once_with(self.mock_context, "test_char_id", 1, "{}", "{}", 0) # Removido

        self.mock_context.send.assert_called_once_with("Erro ao subir de nível: Erro de lógica de nível.")

if __name__ == '__main__':
    unittest.main()