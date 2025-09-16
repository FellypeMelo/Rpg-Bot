import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

@dataclass
class CombatSession:
    character_id: str
    guild_id: str
    channel_id: str
    player_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str = field(default_factory=lambda: (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat())
    temporary_attributes: Dict = field(default_factory=dict)
    is_active: bool = True

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
        )