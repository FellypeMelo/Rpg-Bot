from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any

@dataclass
class CreateCharacterDTO:
    name: str
    class_name: str
    alias: Optional[str] = None
    base_attributes: Optional[Dict[str, int]] = None

@dataclass
class UpdateCharacterDTO:
    character_id: str
    field_name: str
    value: Any # This will be validated by the service layer

@dataclass
class CharacterResponseDTO:
    id: str
    name: str
    alias: Optional[str]
    class_name: str
    level: int
    experience: int
    attributes: Dict[str, int]
    modifiers: Dict[str, int]
    hp: int
    max_hp: int
    chakra: int
    max_chakra: int
    fp: int
    max_fp: int
    masteries: Dict[str, int]
    ph_points: int
    status_points: int
    mastery_points: int
    inventory: List[str]
    skills: List[str]
    spells: List[str]
    equipment: Dict[str, str]
    created_at: str
    updated_at: str