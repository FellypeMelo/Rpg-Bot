from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PlayerPreferences:
    player_discord_id: str
    favorite_character_id: Optional[str] = None
    command_prefix: str = "!"