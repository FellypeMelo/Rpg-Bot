import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from src.core.services.combat_service import CombatService
from src.core.entities.character import Character
from src.core.entities.combat_session import CombatSession
from src.utils.exceptions.application_exceptions import CombatError, CombatSessionNotFoundError, CharacterNotFoundError, MaxCombatSessionsError, InvalidInputError

class TestCombatService(unittest.TestCase):

    def setUp(self):
        self.mock_character_repository = MagicMock()
        self.mock_session_repository = MagicMock()
        self.combat_service = CombatService(self.mock_character_repository, self.mock_session_repository)

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

    def test_start_combat_session_success(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        self.mock_session_repository.get_all_combat_sessions.return_value = []
        self.mock_session_repository.save_combat_session.return_value = True

        session = self.combat_service.start_combat_session(
            self.mock_character.id, "guild456", "channel789", "player001"
        )

        self.assertIsNotNone(session.id)
        self.assertEqual(session.character_id, self.mock_character.id)
        self.assertEqual(session.player_id, "player001")
        self.mock_character_repository.get_character.assert_called_once_with(self.mock_character.id)
        self.mock_session_repository.get_all_combat_sessions.assert_called_once_with()
        self.mock_session_repository.save_combat_session.assert_called_once()
        self.assertIn("hp", session.temporary_attributes)

    def test_start_combat_session_character_not_found(self):
        self.mock_character_repository.get_character.return_value = None
        with self.assertRaises(CharacterNotFoundError):
            self.combat_service.start_combat_session("non_existent_char", "g", "c", "p")

    def test_start_combat_session_max_sessions_reached(self):
        self.mock_character_repository.get_character.return_value = self.mock_character
        # Simulate 3 active sessions
        self.mock_session_repository.get_all_combat_sessions.return_value = [
            MagicMock(player_id="player001", is_active=True, expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()),
            MagicMock(player_id="player001", is_active=True, expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()),
            MagicMock(player_id="player001", is_active=True, expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat())
        ]
        with self.assertRaises(MaxCombatSessionsError):
            self.combat_service.start_combat_session(self.mock_character.id, "g", "c", "player001")

    def test_get_combat_session_success(self):
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        self.mock_session_repository.update_combat_session.return_value = True
        
        session = self.combat_service.get_combat_session(self.mock_combat_session.id)
        self.assertEqual(session.id, self.mock_combat_session.id)
        self.mock_session_repository.get_combat_session.assert_called_once_with(self.mock_combat_session.id)
        self.mock_session_repository.update_combat_session.assert_called_once_with(session)
        # Check if update_activity was called
        self.assertGreater(datetime.fromisoformat(session.last_activity), datetime.fromisoformat(self.mock_combat_session.start_time))

    def test_get_combat_session_not_found(self):
        self.mock_session_repository.get_combat_session.return_value = None
        with self.assertRaises(CombatSessionNotFoundError):
            self.combat_service.get_combat_session("non_existent_session")

    def test_get_combat_session_inactive(self):
        inactive_session = CombatSession(
            character_id="char123", guild_id="g", channel_id="c", player_id="p", is_active=False
        )
        self.mock_session_repository.get_combat_session.return_value = inactive_session
        with self.assertRaises(CombatSessionNotFoundError):
            self.combat_service.get_combat_session(inactive_session.id)

    def test_apply_damage_hp(self):
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        self.mock_session_repository.update_combat_session.return_value = True
        
        initial_hp = self.mock_combat_session.temporary_attributes["hp"]
        updated_session = self.combat_service.apply_damage(self.mock_combat_session.id, "hp", 20)
        self.assertEqual(updated_session.temporary_attributes["hp"], initial_hp - 20)
        # Called twice: once in get_combat_session and once in apply_damage
        self.assertEqual(self.mock_session_repository.update_combat_session.call_count, 2)

    def test_apply_damage_hp_below_zero(self):
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        self.mock_session_repository.update_combat_session.return_value = True
        
        updated_session = self.combat_service.apply_damage(self.mock_combat_session.id, "hp", 150)
        self.assertEqual(updated_session.temporary_attributes["hp"], 0)

    def test_apply_damage_invalid_attribute_type(self):
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        with self.assertRaises(InvalidInputError):
            self.combat_service.apply_damage(self.mock_combat_session.id, "mana", 10)

    def test_apply_damage_negative_value(self):
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        with self.assertRaises(InvalidInputError):
            self.combat_service.apply_damage(self.mock_combat_session.id, "hp", -10)

    def test_apply_healing_hp(self):
        self.mock_combat_session.temporary_attributes["hp"] = 50
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        self.mock_session_repository.update_combat_session.return_value = True
        
        updated_session = self.combat_service.apply_healing(self.mock_combat_session.id, "hp", 30)
        self.assertEqual(updated_session.temporary_attributes["hp"], 80)
        # Called twice: once in get_combat_session and once in apply_healing
        self.assertEqual(self.mock_session_repository.update_combat_session.call_count, 2)

    def test_apply_healing_hp_above_max(self):
        self.mock_combat_session.temporary_attributes["hp"] = 90
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        self.mock_session_repository.update_combat_session.return_value = True
        
        updated_session = self.combat_service.apply_healing(self.mock_combat_session.id, "hp", 30)
        self.assertEqual(updated_session.temporary_attributes["hp"], self.mock_combat_session.temporary_attributes["max_hp"])

    def test_apply_healing_invalid_attribute_type(self):
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        with self.assertRaises(InvalidInputError):
            self.combat_service.apply_healing(self.mock_combat_session.id, "stamina", 10)

    def test_apply_healing_negative_value(self):
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        with self.assertRaises(InvalidInputError):
            self.combat_service.apply_healing(self.mock_combat_session.id, "hp", -10)

    def test_end_combat_session_discard_changes(self):
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        self.mock_session_repository.delete_combat_session.return_value = True
        
        result = self.combat_service.end_combat_session(self.mock_combat_session.id, persist_changes=False)
        self.assertTrue(result)
        self.assertFalse(self.mock_combat_session.is_active)
        self.mock_session_repository.delete_combat_session.assert_called_once_with(self.mock_combat_session.id)
        self.mock_character_repository.update_character.assert_not_called()

    def test_end_combat_session_persist_changes(self):
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        self.mock_character_repository.get_character.return_value = self.mock_character
        self.mock_character_repository.update_character.return_value = True
        self.mock_session_repository.delete_combat_session.return_value = True

        # Simulate some changes in temporary attributes
        self.mock_combat_session.temporary_attributes["hp"] = 70
        self.mock_combat_session.temporary_attributes["chakra"] = 30

        result = self.combat_service.end_combat_session(self.mock_combat_session.id, persist_changes=True)
        self.assertTrue(result)
        self.assertFalse(self.mock_combat_session.is_active)
        self.mock_session_repository.delete_combat_session.assert_called_once_with(self.mock_combat_session.id)
        self.mock_character_repository.update_character.assert_called_once()
        self.assertEqual(self.mock_character.hp, 70)
        self.assertEqual(self.mock_character.chakra, 30)

    def test_end_combat_session_persist_changes_character_not_found(self):
        self.mock_session_repository.get_combat_session.return_value = self.mock_combat_session
        self.mock_character_repository.get_character.return_value = None
        with self.assertRaises(CharacterNotFoundError):
            self.combat_service.end_combat_session(self.mock_combat_session.id, persist_changes=True)

    def test_get_active_combat_sessions_by_player(self):
        session1 = CombatSession(character_id="c1", guild_id="g1", channel_id="ch1", player_id="p1", is_active=True, expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat())
        session2 = CombatSession(character_id="c2", guild_id="g1", channel_id="ch2", player_id="p1", is_active=True, expires_at=(datetime.now(timezone.utc) + timedelta(hours=2)).isoformat())
        session3_inactive = CombatSession(character_id="c3", guild_id="g1", channel_id="ch3", player_id="p1", is_active=False, expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat())
        session4_expired = CombatSession(character_id="c4", guild_id="g1", channel_id="ch4", player_id="p1", is_active=True, expires_at=(datetime.now(timezone.utc) - timedelta(hours=1)).isoformat())
        session5_other_player = CombatSession(character_id="c5", guild_id="g1", channel_id="ch5", player_id="p2", is_active=True, expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat())

        self.mock_session_repository.get_all_combat_sessions.return_value = [
            session1, session2, session3_inactive, session4_expired, session5_other_player
        ]

        active_sessions = self.combat_service.get_active_combat_sessions_by_player("p1")
        self.assertEqual(len(active_sessions), 2)
        self.assertIn(session1, active_sessions)
        self.assertIn(session2, active_sessions)
        self.assertNotIn(session3_inactive, active_sessions)
        self.assertNotIn(session4_expired, active_sessions)
        self.assertNotIn(session5_other_player, active_sessions)

if __name__ == '__main__':
    unittest.main()