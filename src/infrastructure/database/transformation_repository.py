from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.core.entities.transformation import Transformation
from src.utils.exceptions.infrastructure_exceptions import DatabaseConnectionError
from bson.objectid import ObjectId
from typing import Optional

class TransformationRepository:
    def __init__(self, mongodb_repository: MongoDBRepository):
        self.mongodb_repository = mongodb_repository
        self.collection = mongodb_repository.transformacoes_collection

    async def save_transformation(self, transformation: Transformation) -> str:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de transformações não estabelecida.")
        transformation_dict = transformation.to_dict()
        result = await self.collection.insert_one(transformation_dict)
        return str(result.inserted_id)

    async def get_transformation(self, transformation_id: str) -> Optional[Transformation]:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de transformações não estabelecida.")
        data = await self.collection.find_one({"id": transformation_id})
        if data:
            return Transformation.from_dict(data)
        return None

    async def get_transformation_by_name(self, name: str) -> Optional[Transformation]:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de transformações não estabelecida.")
        data = await self.collection.find_one({"name": name})
        if data:
            return Transformation.from_dict(data)
        return None

    async def update_transformation(self, transformation: Transformation) -> bool:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de transformações não estabelecida.")
        transformation_dict = transformation.to_dict()
        result = await self.collection.replace_one({"id": transformation.id}, transformation_dict)
        return result.modified_count > 0

    async def delete_transformation(self, transformation_id: str) -> bool:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de transformações não estabelecida.")
        result = await self.collection.delete_one({"id": transformation_id})
        return result.deleted_count > 0