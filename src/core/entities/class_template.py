from dataclasses import dataclass, field
from typing import Dict, List, Any
from bson.objectid import ObjectId

@dataclass
class ClassTemplate:
    name: str
    description: str
    id: ObjectId = field(default_factory=ObjectId)
    base_attributes: Dict[str, int] = field(default_factory=lambda: {
        "strength": 10, "dexterity": 10, "constitution": 10,
        "intelligence": 10, "wisdom": 10, "charisma": 10
    })
    hp_formula: str = "1d1"
    chakra_formula: str = "1d1"
    fp_formula: str = "1d1"
    starting_masteries: Dict[str, int] = field(default_factory=dict)
    starting_skills: List[str] = field(default_factory=list)
    starting_spells: List[str] = field(default_factory=list)
    level_up_bonuses: Dict[str, Any] = field(default_factory=lambda: {
        "status_points": 3,
        "mastery_points": 2,
        "ph_points": 1
    })

    def to_dict(self):
        return {
            "_id": str(self.id),
            "name": self.name,
            "description": self.description,
            "base_attributes": self.base_attributes,
            "hp_formula": self.hp_formula,
            "chakra_formula": self.chakra_formula,
            "fp_formula": self.fp_formula,
            "starting_masteries": self.starting_masteries,
            "starting_skills": self.starting_skills,
            "starting_spells": self.starting_spells,
            "level_up_bonuses": self.level_up_bonuses,
        }

    @staticmethod
    def from_dict(data: Dict):
        # Accept multiple possible key names to be tolerant with existing DB documents
        raw_id = data.get("_id") or data.get("id")
        # name may be stored as 'name' or 'nome'
        name = data.get("name") or data.get("nome") or "Unknown"
        description = data.get("description") or data.get("descricao") or ""

        return ClassTemplate(
            id=ObjectId(raw_id) if raw_id is not None else ObjectId(),
            name=name,
            description=description,
            base_attributes=data.get("base_attributes", {}),
            hp_formula=data.get("hp_formula", "1d1"),
            chakra_formula=data.get("chakra_formula", "1d1"),
            fp_formula=data.get("fp_formula", "1d1"),
            starting_masteries=data.get("starting_masteries", {}),
            starting_skills=data.get("starting_skills", []),
            starting_spells=data.get("starting_spells", []),
            level_up_bonuses=data.get("level_up_bonuses", {
                "status_points": 3,
                "mastery_points": 2,
                "ph_points": 1
            }),
        )