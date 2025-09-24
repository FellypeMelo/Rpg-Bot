from typing import List, Dict, Any
from src.core.entities.character import Character
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.utils.exceptions.application_exceptions import CharacterNotFoundError

class ReportService:
    def __init__(self, character_repository: MongoDBRepository):
        self.character_repository = character_repository

    async def get_progress_report(self, character_id: str) -> Dict[str, Any]:
        character = await self.character_repository.get_character(character_id)
        if not character:
            raise CharacterNotFoundError(f"Personagem com ID '{character_id}' não encontrado.")

        # This is a simplified report. In a real scenario, we would store historical data
        # for levels gained, points distributed, etc. For now, it reflects current state.
        report = {
            "character_name": character.name,
            "level": character.level,
            "experience": character.experience,
            "attributes": character.attributes,
            "modifiers": character.modifiers,
            "masteries": character.masteries,
            "ph_points": character.pontos.get("ph", {}).get("total", 0),
            "status_points_available": character.pontos.get("status", {}).get("total", 0),
            "mastery_points_available": character.pontos.get("mastery", {}).get("total", 0),
            "hp": f"{character.hp}/{character.max_hp}",
            "chakra": f"{character.chakra}/{character.max_chakra}",
            "fp": f"{character.fp}/{character.max_fp}",
            "last_updated": character.updated_at
        }
        return report

    async def get_usage_statistics(self) -> Dict[str, Any]:
        all_characters = await self.character_repository.get_all_characters()
        
        total_characters = len(all_characters)
        
        # Example statistics (can be expanded)
        class_distribution = {}
        total_levels = 0
        for char in all_characters:
            class_distribution[char.class_name] = class_distribution.get(char.class_name, 0) + 1
            total_levels += char.level

        avg_level = total_levels / total_characters if total_characters > 0 else 0

        stats = {
            "total_characters": total_characters,
            "class_distribution": class_distribution,
            "average_character_level": round(avg_level, 2),
            # Add more statistics as needed, e.g., most used commands (requires logging integration)
        }
        return stats