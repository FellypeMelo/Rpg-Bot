from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import re
from typing import Dict, List, Optional
from src.core.entities.character import Character
from src.utils.exceptions.infrastructure_exceptions import DatabaseConnectionError, RepositoryError

class MongoDBRepository:
    def __init__(self, connection_string: str, database_name: str, collection_name: str):
        self.connection_string = connection_string
        self.database_name = database_name
        self.collection_name = collection_name
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            self.client.admin.command('ping') # Test connection
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            print(f"Conectado ao MongoDB: {self.database_name}/{self.collection_name}")
        except ConnectionFailure as e:
            raise DatabaseConnectionError(f"Falha ao conectar ao MongoDB: {e}")
        except Exception as e:
            raise DatabaseConnectionError(f"Erro inesperado ao conectar ao MongoDB: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Desconectado do MongoDB.")

    def save_character(self, character: Character) -> str:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com o MongoDB não estabelecida.")
        try:
            character_dict = character.to_dict()
            result = self.collection.insert_one(character_dict)
            if not result.acknowledged:
                raise RepositoryError("Falha ao salvar personagem: operação não reconhecida.")
            return str(result.inserted_id)
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao salvar personagem: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao salvar personagem: {e}")

    def get_character(self, character_id: str) -> Optional[Character]:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com o MongoDB não estabelecida.")
        try:
            data = self.collection.find_one({"id": character_id})
            if data:
                return Character.from_dict(data)
            return None
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar personagem: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar personagem: {e}")

    def get_character_by_name_or_alias(self, name_or_alias: str) -> Optional[Character]:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com o MongoDB não estabelecida.")
        try:
            # Case-insensitive search for name or alias
            data = self.collection.find_one({
                "$or": [
                    {"name": {"$regex": f"^{re.escape(name_or_alias)}$", "$options": "i"}},
                    {"alias": {"$regex": f"^{re.escape(name_or_alias)}$", "$options": "i"}}
                ]
            })
            if data:
                return Character.from_dict(data)
            return None
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar personagem por nome/apelido: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar personagem por nome/apelido: {e}")

    def update_character(self, character: Character) -> bool:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com o MongoDB não estabelecida.")
        try:
            character_dict = character.to_dict()
            result = self.collection.replace_one({"id": character.id}, character_dict)
            if not result.acknowledged:
                raise RepositoryError("Falha ao atualizar personagem: operação não reconhecida.")
            return result.modified_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao atualizar personagem: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao atualizar personagem: {e}")

    def delete_character(self, character_id: str) -> bool:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com o MongoDB não estabelecida.")
        try:
            result = self.collection.delete_one({"id": character_id})
            if not result.acknowledged:
                raise RepositoryError("Falha ao deletar personagem: operação não reconhecida.")
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao deletar personagem: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao deletar personagem: {e}")

    def get_all_characters(self) -> List[Character]:
        if self.collection is None:
            raise DatabaseConnectionError("Conexão com o MongoDB não estabelecida.")
        try:
            characters = []
            for data in self.collection.find():
                characters.append(Character.from_dict(data))
            return characters
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar todos os personagens: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar todos os personagens: {e}")