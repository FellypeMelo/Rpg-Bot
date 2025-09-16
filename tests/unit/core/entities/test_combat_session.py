import unittest
from datetime import datetime, timedelta, timezone
from src.core.entities.combat_session import CombatSession
from unittest.mock import patch, MagicMock

class TestCombatSession(unittest.TestCase):

    def setUp(self):
        self.session_data = {
            "character_id": "char123",
            "guild_id": "guild456",
            "channel_id": "channel789",
            "player_id": "player001",
            "temporary_attributes": {"hp": 80, "max_hp": 100}
        }
        self.combat_session = CombatSession(**self.session_data)

    def test_combat_session_creation(self):
        self.assertIsNotNone(self.combat_session.id)
        self.assertEqual(self.combat_session.character_id, "char123")
        self.assertEqual(self.combat_session.guild_id, "guild456")
        self.assertEqual(self.combat_session.channel_id, "channel789")
        self.assertEqual(self.combat_session.player_id, "player001")
        self.assertTrue(self.combat_session.is_active)
        self.assertIn("hp", self.combat_session.temporary_attributes)
        self.assertIsInstance(datetime.fromisoformat(self.combat_session.start_time), datetime)
        self.assertIsInstance(datetime.fromisoformat(self.combat_session.last_activity), datetime)
        self.assertIsInstance(datetime.fromisoformat(self.combat_session.expires_at), datetime)
        self.assertGreater(datetime.fromisoformat(self.combat_session.expires_at), datetime.fromisoformat(self.combat_session.start_time))

    def test_update_activity(self):
        old_last_activity = self.combat_session.last_activity
        old_expires_at = self.combat_session.expires_at
        self.combat_session.update_activity()
        self.assertGreater(datetime.fromisoformat(self.combat_session.last_activity), datetime.fromisoformat(old_last_activity))
        self.assertGreater(datetime.fromisoformat(self.combat_session.expires_at), datetime.fromisoformat(old_expires_at))
        self.assertAlmostEqual(
            datetime.fromisoformat(self.combat_session.expires_at),
            datetime.now(timezone.utc) + timedelta(hours=4),
            delta=timedelta(seconds=5) # Allow for small time differences
        )

    def test_to_dict_method(self):
        session_dict = self.combat_session.to_dict()
        self.assertIsInstance(session_dict, dict)
        self.assertEqual(session_dict["character_id"], "char123")
        self.assertEqual(session_dict["id"], self.combat_session.id)
        self.assertIn("temporary_attributes", session_dict)

    def test_from_dict_method(self):
        session_dict = self.combat_session.to_dict()
        new_session = CombatSession.from_dict(session_dict)
        self.assertEqual(new_session.id, self.combat_session.id)
        self.assertEqual(new_session.character_id, self.combat_session.character_id)
        self.assertEqual(new_session.guild_id, self.combat_session.guild_id)
        self.assertEqual(new_session.temporary_attributes["hp"], self.combat_session.temporary_attributes["hp"])

if __name__ == '__main__':
    unittest.main()