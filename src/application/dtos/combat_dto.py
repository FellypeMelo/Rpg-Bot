from dataclasses import dataclass, field
from typing import Optional, Dict, List

@dataclass
class StartCombatSessionDTO:
    character_id: str
    guild_id: str
    channel_id: str
    player_id: str

@dataclass
class ApplyDamageHealingDTO:
    session_id: str
    attribute_type: str
    value: int

@dataclass
class EndCombatSessionDTO:
    session_id: str
    persist_changes: bool = False

@dataclass
class CombatSessionResponseDTO:
    id: str
    character_id: str
    guild_id: str
    channel_id: str
    player_id: str
    start_time: str
    last_activity: str
    expires_at: str
    temporary_attributes: Dict
    is_active: bool