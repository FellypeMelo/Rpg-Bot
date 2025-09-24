from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone
from bson.objectid import ObjectId
from src.core.entities.class_template import ClassTemplate # Importar ClassTemplate

@dataclass
class Character:
    name: str
    # Backwards-compatible: some tests/usage pass `class_name` instead of `player_discord_id`.
    class_name: Optional[str] = None
    player_discord_id: Optional[str] = None
    id: ObjectId = field(default_factory=ObjectId)
    alias: Optional[str] = None
    level: int = 1
    experience: int = 0
    classe_ids: List[ObjectId] = field(default_factory=list)
    titulos: List[str] = field(default_factory=list)
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
    pontos: Dict[str, Dict] = field(default_factory=lambda: {
        "ph": {"total": 0, "gasto": []},
        "status": {"total": 0},
        "mastery": {"total": 0}
    })
    inventory: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    spells: List[str] = field(default_factory=list)
    equipment: Dict[str, str] = field(default_factory=dict)
    transformacoes_disponiveis: List[Dict] = field(default_factory=list)
    transformacoes_ativas: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def calculate_modifiers(self):
        from src.core.calculators.modifier_calc import ModifierCalculator
        self.modifiers = ModifierCalculator.calculate_all_modifiers(self.attributes)

    def roll_class_attributes(self, class_template: ClassTemplate, add_to_existing: bool = False):
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
        self.updated_at = datetime.now(timezone.utc)

    def apply_healing(self, attribute_type: str, value: int):
        if attribute_type == "hp":
            self.hp = min(self.max_hp, self.hp + value)
        elif attribute_type == "chakra":
            self.chakra = min(self.max_chakra, self.chakra + value)
        elif attribute_type == "fp":
            self.fp = min(self.max_fp, self.fp + value)
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self):
        """
        Converts the character object to a dictionary compatible with MongoDB (BSON).
        ObjectIds are kept as is, and datetimes are converted to ISO format strings.
        """
        return {
            "_id": self.id,
            "player_discord_id": self.player_discord_id,
            "name": self.name,
            "alias": self.alias,
            "level": self.level,
            "experience": self.experience,
            "classe_ids": self.classe_ids,
            "titulos": self.titulos,
            "attributes": self.attributes,
            "modifiers": self.modifiers,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "chakra": self.chakra,
            "max_chakra": self.max_chakra,
            "fp": self.fp,
            "max_fp": self.max_fp,
            "masteries": self.masteries,
            "pontos": {
                "ph": {
                    "total": self.pontos.get("ph", {}).get("total", 0),
                    "gasto": [
                        {"descricao": item.get("descricao"), "custo": item.get("custo"), "data": item.get("data").isoformat() if isinstance(item.get("data"), datetime) else item.get("data")}
                        for item in self.pontos.get("ph", {}).get("gasto", [])
                    ]
                },
                "status": {"total": self.pontos.get("status", {}).get("total", 0)},
                "mastery": {"total": self.pontos.get("mastery", {}).get("total", 0)}
            },
            "inventory": self.inventory,
            "skills": self.skills,
            "spells": self.spells,
            "equipment": self.equipment,
            "transformacoes_disponiveis": self.transformacoes_disponiveis,
            "transformacoes_ativas": [
                {
                    "transformacao_id": t.get("transformacao_id"),
                    "nome": t.get("nome"),
                    "activated_at": t.get("activated_at").isoformat() if isinstance(t.get("activated_at"), datetime) else t.get("activated_at"),
                    "expires_at": t.get("expires_at").isoformat() if isinstance(t.get("expires_at"), datetime) else t.get("expires_at"),
                }
                for t in self.transformacoes_ativas
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict):
        def _parse_datetime(value):
            if value is None:
                return None
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value)
                except Exception:
                    return None
            return None

        def _get_objid_list(lst):
            result = []
            for oid in lst:
                try:
                    result.append(ObjectId(oid))
                except Exception:
                    # already an ObjectId or invalid - try to append as-is
                    result.append(oid)
            return result

        pontos_ph_gasto = []
        for item in data.get("pontos", {}).get("ph", {}).get("gasto", []):
            # support both Portuguese keys (descricao,custo,data) and older/english (description,points)
            descricao = item.get("descricao") or item.get("description") or item.get("desc") or ""
            custo = item.get("custo") if item.get("custo") is not None else item.get("points") if item.get("points") is not None else item.get("custo")
            data_val = item.get("data") or item.get("date") or item.get("timestamp")
            pontos_ph_gasto.append({
                "descricao": descricao,
                "custo": custo or 0,
                "data": _parse_datetime(data_val)
            })

        character = Character(
            id=ObjectId(data["_id"]) if data.get("_id") is not None else ObjectId(),
            player_discord_id=data.get("player_discord_id"),
            name=data["name"],
            alias=data.get("alias"),
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            classe_ids=_get_objid_list(data.get("classe_ids", [])),
            titulos=data.get("titulos", []),
            attributes=data.get("attributes", {}),
            modifiers=data.get("modifiers", {}),
            hp=data.get("hp", 0),
            max_hp=data.get("max_hp", 0),
            chakra=data.get("chakra", 0),
            max_chakra=data.get("max_chakra", 0),
            fp=data.get("fp", 0),
            max_fp=data.get("max_fp", 0),
            masteries=data.get("masteries", {}),
            pontos={
                "ph": {
                    "total": data.get("pontos", {}).get("ph", {}).get("total", 0),
                    "gasto": pontos_ph_gasto
                },
                "status": {"total": data.get("pontos", {}).get("status", {}).get("total", 0)},
                "mastery": {"total": data.get("pontos", {}).get("mastery", {}).get("total", 0)}
            },
            inventory=data.get("inventory", []),
            skills=data.get("skills", []),
            spells=data.get("spells", []),
            equipment=data.get("equipment", {}),
            transformacoes_disponiveis=[
                {"transformacao_id": ObjectId(t["transformacao_id"]) if t.get("transformacao_id") is not None else None, "nome": t.get("nome")}
                for t in data.get("transformacoes_disponiveis", [])
            ],
            transformacoes_ativas=[
                {
                    "transformacao_id": ObjectId(t["transformacao_id"]) if t.get("transformacao_id") is not None else None,
                    "nome": t.get("nome"),
                    "activated_at": _parse_datetime(t.get("activated_at")),
                    "expires_at": _parse_datetime(t.get("expires_at")),
                }
                for t in data.get("transformacoes_ativas", [])
            ],
            created_at=_parse_datetime(data.get("created_at")) or datetime.now(timezone.utc),
            updated_at=_parse_datetime(data.get("updated_at")) or datetime.now(timezone.utc),
        )
        return character
