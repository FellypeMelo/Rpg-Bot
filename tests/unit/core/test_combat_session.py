import unittest
from src.core.entities.combat_session import CombatSession
from datetime import datetime, timezone

class TestCombatSessionEntity(unittest.TestCase):
    def test_add_and_sort_initiative_entries(self):
        s = CombatSession(character_id="c1", guild_id="g1", channel_id="ch1", player_id="p1")
        s.add_initiative_entry(name="Goblin", initiative=12, is_npc=True)
        s.add_initiative_entry(name="Renee", initiative=18, owner_id="player_renee")
        s.add_initiative_entry(name="Orc", initiative=15, is_npc=True)
        # Order should be Renée(18), Orc(15), Goblin(12)
        self.assertEqual(s.turn_order[0]["name"], "Renee")
        self.assertEqual(s.turn_order[1]["name"], "Orc")
        self.assertEqual(s.turn_order[2]["name"], "Goblin")

    def test_start_and_advance_turns(self):
        s = CombatSession(character_id="c1", guild_id="g1", channel_id="ch1", player_id="p1")
        s.add_initiative_entry(name="A", initiative=10)
        s.add_initiative_entry(name="B", initiative=5)
        s.start_battle()
        self.assertEqual(s.current_turn_index, 0)
        self.assertEqual(s.current_turn()["name"], "A")
        s.advance_turn()
        self.assertEqual(s.current_turn()["name"], "B")
        s.advance_turn()
        self.assertEqual(s.current_turn()["name"], "A")

    def test_apply_damage_and_healing(self):
        s = CombatSession(character_id="c1", guild_id="g1", channel_id="ch1", player_id="p1")
        s.add_initiative_entry(name="Target", initiative=10, hp=100, max_hp=100)
        # apply damage
        entry = s.apply_damage_to_target("Target", 30)
        self.assertEqual(entry["damage_taken"], 30)
        self.assertEqual(entry["hp"], 70)
        # apply healing less than damage_taken
        entry = s.apply_healing_to_target("Target", 10)
        self.assertEqual(entry["damage_taken"], 20)
        # apply healing more than remaining damage -> heals hp
        entry = s.apply_healing_to_target("Target", 50)
        self.assertEqual(entry["damage_taken"], 0)
        # hp should not exceed max
        self.assertEqual(entry["hp"], 100)

    def test_serialization_roundtrip(self):
        s = CombatSession(character_id="c1", guild_id="g1", channel_id="ch1", player_id="p1")
        s.add_initiative_entry(name="X", initiative=7)
        d = s.to_dict()
        s2 = CombatSession.from_dict(d)
        self.assertEqual(s2.id, s.id)
        self.assertEqual(s2.guild_id, s.guild_id)
        self.assertEqual(len(s2.turn_order), 1)

    def test_redis_serialization_and_factories(self):
        s = CombatSession(character_id="c1", guild_id="g1", channel_id="ch1", player_id="p1")
        s.add_player_entry(character_id="char1", player_id="player1", name="Hero", initiative=18, hp=120, chakra=40, fp=20)
        s.add_npc_entry(name="Goblin", initiative=10)
        redis_dict = s.to_redis_dict()
        # Simulate storing/loading from Redis
        s2 = CombatSession.from_redis_dict(redis_dict)
        self.assertEqual(s2.channel_id, s.channel_id)
        self.assertEqual(len(s2.turn_order), 2)
        # Ensure types are present
        types = {e.get("type") for e in s2.turn_order}
        self.assertIn("player", types)
        self.assertIn("npc", types)

if __name__ == '__main__':
    unittest.main()
