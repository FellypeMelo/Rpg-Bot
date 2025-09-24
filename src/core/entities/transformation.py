from dataclasses import dataclass, field
from typing import List, Dict, Any
from bson.objectid import ObjectId

@dataclass
class Transformation:
    name: str
    description: str
    id: ObjectId = field(default_factory=ObjectId)
    attribute_modifiers: Dict[str, Any] = field(default_factory=dict)
    skills_granted: List[str] = field(default_factory=list)
    abilities_granted: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "attribute_modifiers": self.attribute_modifiers,
            "skills_granted": self.skills_granted,
            "abilities_granted": self.abilities_granted,
        }

    @staticmethod
    def from_dict(data: Dict):
        return Transformation(
            id=ObjectId(data["id"]),
            name=data["name"],
            description=data["description"],
            attribute_modifiers=data.get("attribute_modifiers", {}),
            skills_granted=data.get("skills_granted", []),
            abilities_granted=data.get("abilities_granted", []),
        )