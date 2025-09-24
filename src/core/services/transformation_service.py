from typing import Dict, Any, Optional
from src.core.entities.transformation import Transformation
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.utils.exceptions.application_exceptions import InvalidInputError

class TransformationService:
    def __init__(self, transformation_repository: TransformationRepository):
        self.transformation_repository = transformation_repository

    async def add_transformation_to_character(self, character_name: str, transformation_name: str) -> str:
        # This is a conceptual method. The actual implementation depends on how transformations are linked to characters.
        # For now, this will just be a placeholder.
        return f"Transformation '{transformation_name}' added to character '{character_name}'."

    async def edit_transformation(self, transformation_name: str, updates: Dict[str, Any]) -> str:
        transformation = await self.get_transformation_by_name(transformation_name)
        if not transformation:
            raise InvalidInputError(f"Transformation '{transformation_name}' not found.")
        
        # Update logic here
        # For example: transformation.duration = updates.get('duration', transformation.duration)
        
        await self.transformation_repository.update_transformation(transformation)
        return f"Transformation '{transformation_name}' updated successfully."

    async def get_transformation_by_name(self, transformation_name: str) -> Optional[Transformation]:
        return await self.transformation_repository.get_transformation_by_name(transformation_name)