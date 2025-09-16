import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone

@dataclass
class Character:
    name: str
    class_name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alias: Optional[str] = None
    level: int = 1
    experience: int = 0
    attributes: Dict[str, int] = field(default_factory=lambda: {
        "strength": 10, "dexterity": 10, "constitution": 10,
        "intelligence": 10, "wisdom": 10, "charisma": 10
    })
    modifiers: Dict[str, int] = field(default_factory=lambda: {
        "strength": 0, "dexterity": 0, "constitution": 0,
        "intelligence": 0, "wisdom": 0, "charisma": 0
    })
    hp: int = 0
    max_hp: int = 0
    chakra: int = 0
    max_chakra: int = 0
    fp: int = 0
    max_fp: int = 0
    masteries: Dict[str, int] = field(default_factory=dict)
    ph_points: int = 0 # Ability Points
    status_points: int = 0
    mastery_points: int = 0
    inventory: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    spells: List[str] = field(default_factory=list)
    equipment: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def calculate_modifiers(self):
        from src.core.calculators.modifier_calc import ModifierCalculator
        self.modifiers = ModifierCalculator.calculate_all_modifiers(self.attributes)

    def roll_class_attributes(self, class_template, add_to_existing: bool = False):
        from src.core.calculators.attribute_calc import AttributeCalculator
        rolled_hp, rolled_chakra, rolled_fp = AttributeCalculator.roll_class_attributes(class_template)
        
        if add_to_existing:
            self.hp += rolled_hp
            self.max_hp += rolled_hp
            self.chakra += rolled_chakra
            self.max_chakra += rolled_chakra
            self.fp += rolled_fp
            self.max_fp += rolled_fp
        else:
            self.hp = rolled_hp
            self.max_hp = rolled_hp
            self.chakra = rolled_chakra
            self.max_chakra = rolled_chakra
            self.fp = rolled_fp
            self.max_fp = rolled_fp

    def apply_damage(self, attribute_type: str, value: int):
        if attribute_type == "hp":
            self.hp = max(0, self.hp - value)
        elif attribute_type == "chakra":
            self.chakra = max(0, self.chakra - value)
        elif attribute_type == "fp":
            self.fp = max(0, self.fp - value)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def apply_healing(self, attribute_type: str, value: int):
        if attribute_type == "hp":
            self.hp = min(self.max_hp, self.hp + value)
        elif attribute_type == "chakra":
            self.chakra = min(self.max_chakra, self.chakra + value)
        elif attribute_type == "fp":
            self.fp = min(self.max_fp, self.fp + value)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "alias": self.alias,
            "class_name": self.class_name,
            "level": self.level,
            "experience": self.experience,
            "attributes": self.attributes,
            "modifiers": self.modifiers,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "chakra": self.chakra,
            "max_chakra": self.max_chakra,
            "fp": self.fp,
            "max_fp": self.max_fp,
            "masteries": self.masteries,
            "ph_points": self.ph_points,
            "status_points": self.status_points,
            "mastery_points": self.mastery_points,
            "inventory": self.inventory,
            "skills": self.skills,
            "spells": self.spells,
            "equipment": self.equipment,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: Dict):
        character = Character(
            id=data["id"],
            name=data["name"],
            alias=data.get("alias"),
            class_name=data["class_name"],
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            attributes=data.get("attributes", {}),
            modifiers=data.get("modifiers", {}),
            hp=data.get("hp", 0),
            max_hp=data.get("max_hp", 0),
            chakra=data.get("chakra", 0),
            max_chakra=data.get("max_chakra", 0),
            fp=data.get("fp", 0),
            max_fp=data.get("max_fp", 0),
            masteries=data.get("masteries", {}),
            ph_points=data.get("ph_points", 0),
            status_points=data.get("status_points", 0),
            mastery_points=data.get("mastery_points", 0),
            inventory=data.get("inventory", []),
            skills=data.get("skills", []),
            spells=data.get("spells", []),
            equipment=data.get("equipment", {}),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
        )
        return character