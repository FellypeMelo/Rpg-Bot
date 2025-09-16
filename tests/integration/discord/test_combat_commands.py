import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from discord.ext import commands
from src.application.commands.combat_commands import CombatCommands
from src.core.services.combat_service import CombatService
from src.core.entities.character import Character
from src.core.entities.combat_session import CombatSession
from src.utils.exceptions.application_exceptions import CombatError, CombatSessionNotFoundError, CharacterNotFoundError, MaxCombatSessionsError, InvalidInputError
from datetime import datetime, timedelta

class TestCombatCommands(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_bot = AsyncMock(spec=commands.Bot)
        self.mock_combat_service = MagicMock(spec=CombatService)
        self.combat_commands = CombatCommands(self.mock_bot, self.mock_combat_service)
        # Registrar o comando no mock_bot para que get_command possa encontrá-lo
        await self.mock_bot.add_cog(self.combat_commands)

        self.mock_context = AsyncMock(spec=commands.Context)
        self.mock_context.send = AsyncMock()
        self.mock_context.author = MagicMock(id="player001")
        self.mock_context.guild = MagicMock(id="guild456")
        self.mock_context.channel = MagicMock(id="channel789")
        self.mock_context.command = MagicMock(name="startcombat")
        self.mock_context.bot = self.mock_bot
        
        # Criar o mock_character e mock_combat_session antes de usá-los
        self.mock_character = Character(
            name="TestChar",
            class_name="Warrior",
            attributes={"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
            hp=100, max_hp=100, chakra=50, max_chakra=50, fp=30, max_fp=30
        )
        self.mock_character.id = "char123"

        self.mock_combat_session = CombatSession(
            character_id="char123",
            guild_id="guild456",
            channel_id="channel789",
            player_id="player001",
            temporary_attributes=self.mock_character.to_dict()
        )
        self.mock_combat_session.id = "session_abc"
        
        self.mock_command = AsyncMock()
        self.mock_command.invoke.return_value = self.mock_combat_session
        self.mock_bot.get_command = MagicMock(return_value=self.mock_command)

    async def test_start_combat_success(self):
        self.mock_combat_service.start_combat_session.return_value = self.mock_combat_session

        await self.combat_commands.start_combat.callback(
            self.combat_commands, self.mock_context, self.mock_character.id
        )

        self.mock_combat_service.start_combat_session.assert_called_once_with(
            self.mock_character.id, "guild456", "channel789", "player001"
        )
        self.mock_context.send.assert_called_once_with(
            f"Sessão de combate iniciada para o personagem `{self.mock_character.id}`. ID da sessão: `{self.mock_combat_session.id}`. Expira em: {self.mock_combat_session.expires_at}"
        )

    async def test_start_combat_character_not_found(self):
        self.mock_combat_service.start_combat_session.side_effect = CharacterNotFoundError("Personagem não encontrado.")

        await self.combat_commands.start_combat.callback(
            self.combat_commands, self.mock_context, "non_existent_char"
        )

        self.mock_context.send.assert_called_once_with("Erro ao iniciar combate: Personagem não encontrado.")

    async def test_start_combat_max_sessions_error(self):
        self.mock_combat_service.start_combat_session.side_effect = MaxCombatSessionsError("Máximo de sessões atingido.")

        await self.combat_commands.start_combat.callback(
            self.combat_commands, self.mock_context, self.mock_character.id
        )

        self.mock_context.send.assert_called_once_with("Erro ao iniciar combate: Máximo de sessões atingido.")

    async def test_apply_damage_success(self):
        self.mock_combat_service.apply_damage.return_value = self.mock_combat_session
        self.mock_combat_session.temporary_attributes["hp"] = 80 # Simulate damage applied

        await self.combat_commands.apply_damage_command.callback(
            self.combat_commands, self.mock_context, self.mock_combat_session.id, "hp", 20
        )

        self.mock_combat_service.apply_damage.assert_called_once_with(self.mock_combat_session.id, "hp", 20)
        self.mock_context.send.assert_called_once_with(
            f"Dano de 20 aplicado a HP na sessão `{self.mock_combat_session.id}`. Novo HP: 80"
        )

    async def test_apply_damage_invalid_input(self):
        self.mock_combat_service.apply_damage.side_effect = InvalidInputError("Tipo de atributo inválido.")

        await self.combat_commands.apply_damage_command.callback(
            self.combat_commands, self.mock_context, self.mock_combat_session.id, "mana", 10
        )

        self.mock_context.send.assert_called_once_with("Erro ao aplicar dano: Tipo de atributo inválido.")

    async def test_apply_healing_success(self):
        self.mock_combat_session.temporary_attributes["hp"] = 70
        self.mock_combat_service.apply_healing.return_value = self.mock_combat_session
        self.mock_combat_session.temporary_attributes["hp"] = 85 # Simulate healing applied

        await self.combat_commands.apply_healing_command.callback(
            self.combat_commands, self.mock_context, self.mock_combat_session.id, "hp", 15
        )

        self.mock_combat_service.apply_healing.assert_called_once_with(self.mock_combat_session.id, "hp", 15)
        self.mock_context.send.assert_called_once_with(
            f"Cura de 15 aplicada a HP na sessão `{self.mock_combat_session.id}`. Novo HP: 85"
        )

    async def test_apply_healing_invalid_input(self):
        self.mock_combat_service.apply_healing.side_effect = InvalidInputError("Valor de cura deve ser positivo.")

        await self.combat_commands.apply_healing_command.callback(
            self.combat_commands, self.mock_context, self.mock_combat_session.id, "hp", 0
        )

        self.mock_context.send.assert_called_once_with("Erro ao aplicar cura: Valor de cura deve ser positivo.")

    async def test_end_combat_session_discard_success(self):
        self.mock_combat_service.end_combat_session.return_value = True

        await self.combat_commands.end_combat_session_command.callback(
            self.combat_commands, self.mock_context, self.mock_combat_session.id
        )

        self.mock_combat_service.end_combat_session.assert_called_once_with(self.mock_combat_session.id, False)
        self.mock_context.send.assert_called_once_with(f"Sessão de combate `{self.mock_combat_session.id}` finalizada e mudanças descartadas.")

    async def test_end_combat_session_persist_success(self):
        self.mock_combat_service.end_combat_session.return_value = True

        await self.combat_commands.end_combat_session_command.callback(
            self.combat_commands, self.mock_context, self.mock_combat_session.id, "--persist"
        )

        self.mock_combat_service.end_combat_session.assert_called_once_with(self.mock_combat_session.id, True)
        self.mock_context.send.assert_called_once_with(f"Sessão de combate `{self.mock_combat_session.id}` finalizada e mudanças persistidas no personagem.")

    async def test_end_combat_session_not_found(self):
        self.mock_combat_service.end_combat_session.side_effect = CombatSessionNotFoundError("Sessão não encontrada.")

        await self.combat_commands.end_combat_session_command.callback(
            self.combat_commands, self.mock_context, "non_existent_session"
        )

        self.mock_context.send.assert_called_once_with("Erro ao finalizar combate: Sessão não encontrada.")

if __name__ == '__main__':
    unittest.main()