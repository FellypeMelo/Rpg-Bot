from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.core.entities.player_preferences import PlayerPreferences
from src.utils.exceptions.infrastructure_exceptions import DatabaseConnectionError
from bson.objectid import ObjectId
from typing import Optional

class PlayerPreferencesRepository:
    def __init__(self, mongodb_repository: MongoDBRepository):
        self.mongodb_repository = mongodb_repository
        self.collection = mongodb_repository.player_preferences_collection

    async def get_preferences(self, player_discord_id: str) -> Optional[PlayerPreferences]:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de preferências do jogador não estabelecida.")
        data = await self.collection.find_one({"player_discord_id": player_discord_id})
        if data:
            # Remove o campo '_id' que é adicionado automaticamente pelo MongoDB
            data.pop('_id', None)
            return PlayerPreferences(**data)
        return None

    async def save_preferences(self, preferences: PlayerPreferences) -> None:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de preferências do jogador não estabelecida.")
        preferences_dict = preferences.__dict__
        await self.collection.update_one(
            {"player_discord_id": preferences.player_discord_id},
            {"$set": preferences_dict},
            upsert=True
        )

    async def delete_preferences(self, player_discord_id: str) -> bool:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de preferências do jogador não estabelecida.")
        result = await self.collection.delete_one({"player_discord_id": player_discord_id})
        return result.deleted_count > 0