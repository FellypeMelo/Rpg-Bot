from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.core.entities.class_template import ClassTemplate
from src.utils.exceptions.infrastructure_exceptions import DatabaseConnectionError
from bson.objectid import ObjectId
from typing import Optional

class ClassRepository:
    def __init__(self, mongodb_repository: MongoDBRepository):
        self.mongodb_repository = mongodb_repository
        self.collection = mongodb_repository.classes_collection

    async def save_class(self, class_template: ClassTemplate) -> str:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de classes não estabelecida.")
        class_dict = class_template.to_dict()
        result = await self.collection.insert_one(class_dict)
        return str(result.inserted_id)

    async def get_class(self, class_id: str) -> Optional[ClassTemplate]:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de classes não estabelecida.")
        data = await self.collection.find_one({"_id": ObjectId(class_id)})
        if data:
            return ClassTemplate.from_dict(data)
        return None
    
    async def get_class_by_name(self, class_name: str) -> Optional[ClassTemplate]:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de classes não estabelecida.")
        data = await self.collection.find_one({"nome": class_name})
        if data:
            return ClassTemplate.from_dict(data)
        return None

    async def update_class(self, class_template: ClassTemplate) -> bool:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de classes não estabelecida.")
        class_dict = class_template.to_dict()
        result = await self.collection.update_one({"_id": class_template.id}, {"$set": class_dict})
        return result.modified_count > 0

    async def delete_class(self, class_id: str) -> bool:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de classes não estabelecida.")
        result = await self.collection.delete_one({"_id": ObjectId(class_id)})
        return result.deleted_count > 0