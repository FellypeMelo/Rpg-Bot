import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from src.utils.helpers.datetime_utils import safe_parse_datetime
from typing import Dict, List, Any, Optional

@dataclass
class CombatSession:
    guild_id: str
    channel_id: str
    character_id: Optional[str] = None
    player_id: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str = field(default_factory=lambda: (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat())
    temporary_attributes: Dict = field(default_factory=dict)
    is_active: bool = True
    # Each entry in turn_order should be a dict with at least:
    # {"name": str, "id": Optional[str], "initiative": int, "owner_id": Optional[str],
    #  "hp": Optional[int], "max_hp": Optional[int], "chakra": Optional[int], "fp": Optional[int],
    #  "damage_taken": int}
    turn_order: List[Dict[str, Any]] = field(default_factory=list)
    current_turn_index: int = -1
    turn_number: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_activity(self):
        self.last_activity = datetime.now(timezone.utc).isoformat()
        self.expires_at = (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "character_id": self.character_id,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "player_id": self.player_id,
            "start_time": self.start_time,
            "last_activity": self.last_activity,
            "expires_at": self.expires_at,
            "temporary_attributes": self.temporary_attributes,
            "is_active": self.is_active,
            "turn_order": self.turn_order,
            "current_turn_index": self.current_turn_index,
            "turn_number": self.turn_number,
            "started_at": self.started_at.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict):
        return CombatSession(
            id=data["id"],
            character_id=data["character_id"],
            guild_id=data["guild_id"],
            channel_id=data["channel_id"],
            player_id=data["player_id"],
            start_time=data.get("start_time", datetime.now(timezone.utc).isoformat()),
            last_activity=data.get("last_activity", datetime.now(timezone.utc).isoformat()),
            expires_at=data.get("expires_at", (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat()),
            temporary_attributes=data.get("temporary_attributes", {}),
            is_active=data.get("is_active", True),
            turn_order=data.get("turn_order", []),
            current_turn_index=data.get("current_turn_index", -1),
            turn_number=data.get("turn_number", 0),
            started_at=safe_parse_datetime(data.get("started_at")) or datetime.now(timezone.utc),
        )

    # --- Combat flow helpers ---
    def add_initiative_entry(self, name: str, initiative: int, owner_id: Optional[str] = None, entry_id: Optional[str] = None, hp: Optional[int] = None, max_hp: Optional[int] = None, chakra: Optional[int] = None, fp: Optional[int] = None, is_npc: bool = False):
        entry = {
            "type": "npc" if is_npc else "player",
            "name": name,
            "id": entry_id,
            "player_id": owner_id,
            "initiative": int(initiative),
            "hp": hp,
            "max_hp": max_hp,
            "chakra": chakra,
            "fp": fp,
        }
        self.turn_order.append(entry)
        # Keep turn_order sorted descending by initiative
        self.turn_order.sort(key=lambda e: e.get("initiative", 0), reverse=True)
        return entry

    def add_player_entry(self, character_id: str, player_id: str, name: str, initiative: int, hp: int, chakra: int, fp: int):
        return self.add_initiative_entry(name=name, initiative=initiative, owner_id=player_id, entry_id=character_id, hp=hp, max_hp=hp, chakra=chakra, fp=fp, is_npc=False)

    def add_npc_entry(self, name: str, initiative: int):
        # NPCs start with a baseline HP of 1000 if not specified, can be changed.
        return self.add_initiative_entry(name=name, initiative=initiative, hp=1000, max_hp=1000, is_npc=True)

    def to_redis_dict(self) -> Dict[str, Any]:
        # Convert datetimes to ISO strings and ensure simple types for Redis storage
        return {
            "channel_id": self.channel_id,
            "turn_order": self.turn_order,
            "current_turn_index": self.current_turn_index,
            "turn_number": self.turn_number,
            "started_at": self.started_at.isoformat() if isinstance(self.started_at, datetime) else None,
            "is_active": self.is_active,
            "temporary_attributes": self.temporary_attributes,
            "id": self.id,
        }

    @staticmethod
    def from_redis_dict(data: Dict[str, Any]):
        started = safe_parse_datetime(data.get("started_at"))
        cs = CombatSession(
            character_id=data.get("character_id", ""),
            guild_id=data.get("guild_id", ""),
            channel_id=data.get("channel_id", ""),
            player_id=data.get("player_id", ""),
            id=data.get("id", str(uuid.uuid4())),
            temporary_attributes=data.get("temporary_attributes", {}),
            is_active=data.get("is_active", True),
            turn_order=data.get("turn_order", []),
            current_turn_index=data.get("current_turn_index", -1),
            turn_number=data.get("turn_number", 0),
            started_at=started or datetime.now(timezone.utc),
        )
        return cs

    def start_battle(self) -> Optional[Dict[str, Any]]:
        if not self.turn_order:
            raise ValueError("Cannot start battle with empty turn order")
        self.current_turn_index = 0
        self.turn_number = 1
        self.started_at = datetime.now(timezone.utc)
        self.is_active = True
        return self.get_current_turn_entry()

    def get_current_turn_entry(self) -> Optional[Dict[str, Any]]:
        if 0 <= self.current_turn_index < len(self.turn_order):
            return self.turn_order[self.current_turn_index]
        return None

    def next_turn_entry(self) -> Optional[Dict[str, Any]]:
        if not self.turn_order:
            return None
        
        # Check if it's the start of a new round
        if self.current_turn_index == len(self.turn_order) - 1:
            self.turn_number += 1
            
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        return self.get_current_turn_entry()

    def _find_target(self, target_id: Optional[str], target_name: Optional[str]) -> Optional[Dict[str, Any]]:
        """Finds a target by ID first, then by name."""
        if target_id:
            for entry in self.turn_order:
                if entry.get("id") == target_id:
                    return entry
        # Ensure target_name is not None before iterating and comparing
        if target_name is not None:
            for entry in self.turn_order:
                if entry.get("name") == target_name:
                    return entry
        return None

    def apply_damage_to_target(self, amount: int, target_id: Optional[str] = None, target_name: Optional[str] = None) -> Dict[str, Any]:
        if not target_id and not target_name:
            raise ValueError("Must provide either target_id or target_name")
            
        entry = self._find_target(target_id, target_name)
        if not entry:
            raise KeyError(f"Target '{target_name or target_id}' not found in turn order")

        # NPCs might not have HP, initialize it on first hit.
        if entry.get("hp") is None and entry.get("type") == "npc":
            entry["hp"] = 1000  # Default starting HP for an NPC
            entry["max_hp"] = 1000

        hp = entry.get("hp")
        if hp is not None:
            try:
                new_hp = max(0, int(hp) - int(amount))
                entry["hp"] = new_hp
            except (ValueError, TypeError):
                pass # Keep original HP if conversion fails
        return entry

    def apply_healing_to_target(self, amount: int, target_id: Optional[str] = None, target_name: Optional[str] = None) -> Dict[str, Any]:
        if not target_id and not target_name:
            raise ValueError("Must provide either target_id or target_name")

        entry = self._find_target(target_id, target_name)
        if not entry:
            raise KeyError(f"Target '{target_name or target_id}' not found in turn order")

        hp = entry.get("hp")
        if hp is not None:
            max_hp = entry.get("max_hp")
            try:
                new_hp = int(hp) + int(amount)
                if max_hp is not None:
                    new_hp = min(int(max_hp), new_hp)
                entry["hp"] = new_hp
            except (ValueError, TypeError):
                pass # Keep original HP if conversion fails
        return entry