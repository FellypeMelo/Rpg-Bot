from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class ApplyLevelUpDTO:
    character_id: str
    levels_to_gain: int
    status_points_spent: Dict[str, int] = field(default_factory=dict)
    mastery_points_spent: Dict[str, int] = field(default_factory=dict)
    ph_points_spent: int = 0

@dataclass
class LevelUpResponseDTO:
    character_id: str
    new_level: int
    updated_attributes: Dict[str, int]
    updated_modifiers: Dict[str, int]
    updated_hp: int
    updated_max_hp: int
    updated_chakra: int
    updated_max_chakra: int
    updated_fp: int
    updated_max_fp: int
    updated_masteries: Dict[str, int]
    remaining_ph_points: int
    remaining_status_points: int
    remaining_mastery_points: int