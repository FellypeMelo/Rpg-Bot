from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import random

from src.core.entities.character import Character
from src.core.entities.transformation import Transformation
from src.core.entities.class_template import ClassTemplate
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.infrastructure.database.class_repository import ClassRepository
from src.core.calculators.dice_roller import DiceRoller
from src.utils.helpers.character_parser import parse_character_sheet
from src.utils.exceptions.application_exceptions import CharacterNotFoundError, InvalidInputError
from bson.errors import InvalidId
from bson import ObjectId

class CharacterService:
    def __init__(self, character_repository: MongoDBRepository, 
                 transformation_repository: TransformationRepository,
                 class_repository: ClassRepository):
        self.character_repository = character_repository
        self.transformation_repository = transformation_repository
        self.class_repository = class_repository

    def _roll_initial_attributes(self) -> Dict[str, int]:
        # Simple attribute roll logic for now, can be expanded
        return {
            "strength": random.randint(8, 18),
            "dexterity": random.randint(8, 18),
            "constitution": random.randint(8, 18),
            "intelligence": random.randint(8, 18),
            "wisdom": random.randint(8, 18),
            "charisma": random.randint(8, 18),
        }

    async def create_character(self, name: str, player_discord_id: str, class_name: str) -> Character:
        class_template = await self.class_repository.get_class_by_name(class_name)
        if not class_template:
            raise InvalidInputError(f"Class '{class_name}' not found.")

        attributes = self._roll_initial_attributes()
        
        hp_roll, _ = DiceRoller.roll_dice(class_template.hp_formula)
        chakra_roll, _ = DiceRoller.roll_dice(class_template.chakra_formula)
        fp_roll, _ = DiceRoller.roll_dice(class_template.fp_formula)

        character = Character(
            name=name,
            player_discord_id=player_discord_id,
            class_name=class_name,
            attributes=attributes,
            max_hp=hp_roll,
            hp=hp_roll,
            max_chakra=chakra_roll,
            chakra=chakra_roll,
            max_fp=fp_roll,
            fp=fp_roll,
            classe_ids=[class_template.id],
            pontos={
                "ph": {"total": 0, "gasto": []},
                "status": {"total": 0},
                "mastery": {"total": 0}
            }
        )
        
        character.calculate_modifiers()
        await self.character_repository.save_character(character)
        return character
    
    async def import_character(self, sheet_text: str, player_discord_id: str) -> Character:
        char_data = parse_character_sheet(sheet_text)
        
        class_info = char_data.get("classes", [{}])[0]
        class_name = class_info.get("name")
        class_template = await self.class_repository.get_class(class_name)
        if not class_template:
            raise InvalidInputError(f"Class '{class_name}' not found.")

        character = Character(
            name=char_data.get("name", "N/A"),
            player_discord_id=player_discord_id,
            class_name=class_name,
            level=char_data.get("level", 1),
            attributes=char_data.get("attributes", {}),
            hp=char_data.get("vida_atual", 1),
            max_hp=char_data.get("vida_max", 1),
            chakra=char_data.get("chakra_atual", 1),
            max_chakra=char_data.get("chakra_max", 1),
            fp=char_data.get("fortitude_atual", 1),
            max_fp=char_data.get("fortitude_max", 1),
            classe_ids=[class_template.id],
            pontos={
                "ph": {"total": 0, "gasto": []},
                "status": {"total": 0},
                "mastery": {"total": 0}
            }
        )
        
        character.calculate_modifiers()
        await self.character_repository.save_character(character)
        return character

    async def add_multiclass(self, character_id: str, new_class_name: str) -> Character:
        character = await self.get_character(character_id)
        
        
        new_class_template = await self.class_repository.get_class(new_class_name)
        if not new_class_template:
            raise InvalidInputError(f"Class '{new_class_name}' not found.")
        if new_class_template.id in character.classe_ids:
            raise InvalidInputError("Character already has this class.")

        character.classe_ids.append(new_class_template.id)

        hp_roll, _ = DiceRoller.roll_dice(new_class_template.hp_formula)
        chakra_roll, _ = DiceRoller.roll_dice(new_class_template.chakra_formula)
        fp_roll, _ = DiceRoller.roll_dice(new_class_template.fp_formula)

        character.max_hp += hp_roll
        character.max_chakra += chakra_roll
        character.max_fp += fp_roll
        
        await self.character_repository.update_character(character)
        return character

    async def get_character(self, identifier: str) -> Character:
        character = await self.character_repository.get_character_by_id_or_name(identifier)
        if not character:
            raise CharacterNotFoundError(f"Personagem com identificador '{identifier}' não encontrado.")

        # Apply transformations
        now = datetime.now(timezone.utc)

        character.transformacoes_ativas = [
            t for t in character.transformacoes_ativas if t.get("expires_at") and t["expires_at"] > now
        ]

        effective_attributes = character.attributes.copy()
        add_bonuses = {}
        mult_bonuses = {}

        for active_trans in character.transformacoes_ativas:
            trans_id = active_trans["transformacao_id"]
            transformation = await self.transformation_repository.get_transformation(str(trans_id))
            if not transformation:
                continue

            for attr, mod in transformation.attribute_modifiers.items():
                if isinstance(mod, (int, float)):
                    add_bonuses[attr] = add_bonuses.get(attr, 0) + mod
                elif isinstance(mod, str) and mod.endswith('%'):
                    mult_bonuses[attr] = mult_bonuses.get(attr, 1) * (1 + float(mod[:-1]) / 100)

        for attr, value in add_bonuses.items():
            if attr in effective_attributes:
                effective_attributes[attr] += value
            elif f"max_{attr}" in character.__dict__:
                setattr(character, f"max_{attr}", getattr(character, f"max_{attr}", 0) + value)

        for attr, value in mult_bonuses.items():
            if attr in effective_attributes:
                effective_attributes[attr] *= value
            elif f"max_{attr}" in character.__dict__:
                setattr(character, f"max_{attr}", getattr(character, f"max_{attr}", 0) * value)
        
        effective_character = character
        effective_character.attributes = {k: int(v) for k, v in effective_attributes.items()}
        effective_character.calculate_modifiers()
        
        return effective_character

    async def update_character(self, character_id: str, field_name: str, value: Any) -> Character:
        character = await self.get_character(character_id)
        
        if hasattr(character, field_name):
            setattr(character, field_name, value)
        else:
            raise InvalidInputError(f"Campo '{field_name}' não pode ser atualizado diretamente.")

        # Recalculate modifiers to ensure persisted document has up-to-date modifiers
        try:
            character.calculate_modifiers()
        except Exception:
            print(f"Aviso: falha ao recalcular modificadores para personagem {character_id}.")

        await self.character_repository.update_character(character)
        return character

    async def delete_all_characters(self) -> int:
        return await self.character_repository.delete_all_characters()

    async def delete_character(self, character_id: str) -> bool:
        return await self.character_repository.delete_character(character_id)
        character = await self.get_character(character_id)
        return await self.character_repository.delete_character(str(character.id))

    async def get_all_characters(self) -> List[Character]:
        return await self.character_repository.get_all_characters()

    async def get_character_with_effective_stats(self, identifier: str) -> Optional[Character]:
        """
        Busca um personagem por ID, nome ou alias e calcula seus status efetivos.
        Tenta converter o identificador para ObjectId se for uma string de ID válida.
        """
        character: Optional[Character] = None
        try:
            # Tenta converter para ObjectId. Se for um ID válido, busca por ele.
            char_id = ObjectId(identifier)
            character = await self.character_repository.get_character_by_id(char_id)
        except (InvalidId, TypeError):
            # Se não for um ObjectId válido, busca por nome ou alias.
            character = await self.character_repository.get_character_by_name_or_alias(identifier)

        # Se ainda não encontrou, tenta uma última vez por nome/alias (cobre o caso de um ID válido não encontrado)
        if not character:
            character = await self.character_repository.get_character_by_name_or_alias(identifier)

        if not character:
            return None # Retorna None se não encontrar de nenhuma forma

        now = datetime.now(timezone.utc)

        character.transformacoes_ativas = [
            t for t in character.transformacoes_ativas if t.get("expires_at") and t["expires_at"] > now
        ]

        effective_attributes = character.attributes.copy()
        add_bonuses = {}
        mult_bonuses = {}

        for active_trans in character.transformacoes_ativas:
            trans_id = active_trans["transformacao_id"]
            transformation = await self.transformation_repository.get_transformation(str(trans_id))
            if not transformation:
                continue

            for attr, mod in transformation.attribute_modifiers.items():
                if isinstance(mod, (int, float)):
                    add_bonuses[attr] = add_bonuses.get(attr, 0) + mod
                elif isinstance(mod, str) and mod.endswith('%'):
                    mult_bonuses[attr] = mult_bonuses.get(attr, 1) * (1 + float(mod[:-1]) / 100)

        for attr, value in add_bonuses.items():
            if attr in effective_attributes:
                effective_attributes[attr] += value
            elif f"max_{attr}" in character.__dict__:
                setattr(character, f"max_{attr}", getattr(character, f"max_{attr}", 0) + value)

        for attr, value in mult_bonuses.items():
            if attr in effective_attributes:
                effective_attributes[attr] *= value
            elif f"max_{attr}" in character.__dict__:
                setattr(character, f"max_{attr}", getattr(character, f"max_{attr}", 0) * value)
        
        effective_character = character
        effective_character.attributes = {k: int(v) for k, v in effective_attributes.items()}
        effective_character.calculate_modifiers()
        
        return effective_character

    async def edit_transformation(self, transformation_id: str, updates: Dict[str, Any]) -> Transformation:
        transformation = await self.transformation_repository.get_transformation(transformation_id)
        if not transformation:
            raise InvalidInputError("Transformation not found")

        for key, value in updates.items():
            if hasattr(transformation, key):
                setattr(transformation, key, value)

        await self.transformation_repository.update_transformation(transformation)
        return transformation

    async def activate_transformation(self, character_id: str, transformation_id: str, duration_seconds: int) -> Character:
        character = await self.get_character(character_id)
        transformation = await self.transformation_repository.get_transformation(transformation_id)
        if not transformation:
            raise InvalidInputError("Transformation not found")

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
        
        active_transformation = {
            "transformacao_id": transformation.id,
            "expires_at": expires_at,
            "nome": transformation.name
        }

        character.transformacoes_ativas.append(active_transformation)
        await self.character_repository.update_character(character)
        return character

    # This was a duplicated method. Removing it.

    async def deactivate_transformation(self, character_id: str, transformation_id: str) -> Character:
        character = await self.get_character(character_id)
        
        initial_len = len(character.transformacoes_ativas)
        character.transformacoes_ativas = [
            t for t in character.transformacoes_ativas if str(t["transformacao_id"]) != transformation_id
        ]

        if len(character.transformacoes_ativas) == initial_len:
            raise InvalidInputError("Active transformation not found on character")

        await self.character_repository.update_character(character)
        return character