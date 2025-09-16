import unittest
from unittest.mock import patch, MagicMock
import redis
import json
from datetime import datetime, timedelta
from src.infrastructure.cache.redis_repository import RedisRepository
from src.core.entities.combat_session import CombatSession
from src.utils.exceptions.infrastructure_exceptions import CacheError, DatabaseConnectionError
from typing import cast

class TestRedisRepository(unittest.TestCase):

    @patch('redis.Redis')
    def setUp(self, MockRedis):
        self.mock_redis_client = MockRedis.return_value
        self.mock_redis_client.ping.return_value = True
        self.mock_redis_client.get.return_value = None
        self.mock_redis_client.setex.return_value = True
        self.mock_redis_client.delete.return_value = 1
        self.mock_redis_client.ttl.return_value = 3600 # Default TTL of 1 hour

        self.repo = RedisRepository(host='localhost', port=6379, db=0)
        self.repo.client = self.mock_redis_client # Ensure the mock is used

        self.session_data = {
            "character_id": "char123",
            "guild_id": "guild456",
            "channel_id": "channel789",
            "player_id": "player001",
            "temporary_attributes": {"hp": 80, "max_hp": 100}
        }
        self.combat_session = CombatSession(**self.session_data)

    def test_connection_success(self):
        self.mock_redis_client.ping.assert_called_once()
        self.assertIsNotNone(self.repo.client)

    @patch('redis.Redis', side_effect=redis.ConnectionError("Test connection failure"))
    def test_connection_failure(self, MockRedis):
        with self.assertRaises(DatabaseConnectionError):
            RedisRepository(host='localhost', port=6379, db=0)

    def test_save_combat_session(self):
        ttl = 3600
        result = self.repo.save_combat_session(self.combat_session, ttl)
        self.assertTrue(result)
        self.mock_redis_client.setex.assert_called_once_with(
            f"combat_session:{self.combat_session.id}", ttl, json.dumps(self.combat_session.to_dict())
        )

    def test_get_combat_session(self):
        session_dict = self.combat_session.to_dict()
        self.mock_redis_client.get.return_value = json.dumps(session_dict)

        retrieved_session = self.repo.get_combat_session(self.combat_session.id)
        self.assertIsNotNone(retrieved_session)
        retrieved_session = cast(CombatSession, retrieved_session)
        self.assertEqual(retrieved_session.id, self.combat_session.id)
        self.assertEqual(retrieved_session.character_id, self.combat_session.character_id)
        self.mock_redis_client.get.assert_called_once_with(f"combat_session:{self.combat_session.id}")

    def test_get_combat_session_not_found(self):
        self.mock_redis_client.get.return_value = None
        retrieved_session = self.repo.get_combat_session("non_existent_id")
        self.assertIsNone(retrieved_session)

    def test_update_combat_session(self):
        session_dict = self.combat_session.to_dict()
        self.mock_redis_client.get.return_value = json.dumps(session_dict) # Simulate existing session
        self.mock_redis_client.ttl.return_value = 1800 # Simulate remaining TTL

        self.combat_session.temporary_attributes["hp"] = 70
        result = self.repo.update_combat_session(self.combat_session)
        self.assertTrue(result)
        self.mock_redis_client.setex.assert_called_once_with(
            f"combat_session:{self.combat_session.id}", 1800, json.dumps(self.combat_session.to_dict())
        )

    def test_update_combat_session_not_found(self):
        self.mock_redis_client.ttl.return_value = -2 # Key does not exist
        result = self.repo.update_combat_session(self.combat_session)
        self.assertFalse(result)

    def test_update_combat_session_no_expire(self):
        session_dict = self.combat_session.to_dict()
        self.mock_redis_client.get.return_value = json.dumps(session_dict)
        self.mock_redis_client.ttl.return_value = -1 # Key exists but no expire

        self.combat_session.temporary_attributes["hp"] = 60
        result = self.repo.update_combat_session(self.combat_session)
        self.assertTrue(result)
        # Should set a default TTL of 4 hours (14400 seconds)
        self.mock_redis_client.setex.assert_called_once_with(
            f"combat_session:{self.combat_session.id}", int(timedelta(hours=4).total_seconds()), json.dumps(self.combat_session.to_dict())
        )

    def test_delete_combat_session(self):
        result = self.repo.delete_combat_session(self.combat_session.id)
        self.assertTrue(result)
        self.mock_redis_client.delete.assert_called_once_with(f"combat_session:{self.combat_session.id}")

    def test_delete_combat_session_not_found(self):
        self.mock_redis_client.delete.return_value = 0
        result = self.repo.delete_combat_session("non_existent_id")
        self.assertFalse(result)

    @patch('src.infrastructure.cache.redis_repository.RedisRepository._connect')
    def test_cache_error_on_save(self, mock_connect):
        self.repo.client = None # Simulate disconnected client
        with self.assertRaises(CacheError):
            self.repo.save_combat_session(self.combat_session, 3600)

    @patch('src.infrastructure.cache.redis_repository.RedisRepository._connect')
    def test_cache_error_on_get(self, mock_connect):
        self.repo.client = None # Simulate disconnected client
        with self.assertRaises(CacheError):
            self.repo.get_combat_session("some_id")

    def test_get_all_combat_sessions(self):
        session1 = CombatSession(character_id="char1", guild_id="g1", channel_id="c1", player_id="p1")
        session2 = CombatSession(character_id="char2", guild_id="g2", channel_id="c2", player_id="p2")

        self.mock_redis_client.scan_iter.return_value = [
            f"combat_session:{session1.id}".encode('utf-8'),
            f"combat_session:{session2.id}".encode('utf-8')
        ]
        self.mock_redis_client.get.side_effect = [
            json.dumps(session1.to_dict()).encode('utf-8'),
            json.dumps(session2.to_dict()).encode('utf-8')
        ]

        sessions = self.repo.get_all_combat_sessions()
        self.assertEqual(len(sessions), 2)
        self.assertTrue(any(s.character_id == "char1" for s in sessions))
        self.assertTrue(any(s.character_id == "char2" for s in sessions))
        self.mock_redis_client.scan_iter.assert_called_once_with("combat_session:*")
        self.assertEqual(self.mock_redis_client.get.call_count, 2)

if __name__ == '__main__':
    unittest.main()