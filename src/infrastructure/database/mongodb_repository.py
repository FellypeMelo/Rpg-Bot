from pymongo.errors import ConnectionFailure, PyMongoError
import re
from typing import Dict, List, Optional, Any, Union
from bson.objectid import ObjectId
from src.core.entities.character import Character
from src.core.entities.class_template import ClassTemplate
from src.core.entities.player_preferences import PlayerPreferences
from src.core.entities.transformation import Transformation
from src.utils.exceptions.infrastructure_exceptions import DatabaseConnectionError, RepositoryError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

class MongoDBRepository:
    def __init__(self, connection_string: str, database_name: str):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.characters_collection: Optional[AsyncIOMotorCollection] = None
        self.classes_collection: Optional[AsyncIOMotorCollection] = None
        self.titulos_collection: Optional[AsyncIOMotorCollection] = None
        self.player_preferences_collection: Optional[AsyncIOMotorCollection] = None
        self.transformacoes_collection: Optional[AsyncIOMotorCollection] = None
        # A conexão será feita de forma assíncrona quando o bot for iniciado

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            assert self.client is not None # Garante que self.client não é None
            # Test connection
            await self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.characters_collection = self.db["characters"]
            self.classes_collection = self.db["classes"]
            self.titulos_collection = self.db["titulos"]
            self.player_preferences_collection = self.db["player_preferences"]
            self.transformacoes_collection = self.db["transformacoes"]
            print(f"Conectado ao MongoDB: {self.database_name}")
        except ConnectionFailure as e:
            raise DatabaseConnectionError(f"Falha ao conectar ao MongoDB: {e}")
        except Exception as e:
            raise DatabaseConnectionError(f"Erro inesperado ao conectar ao MongoDB: {e}")

    def __enter__(self):
        # Este método não será usado para operações assíncronas, mas é mantido para compatibilidade
        raise NotImplementedError("Use async context manager for MongoDBRepository")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Este método não será usado para operações assíncronas, mas é mantido para compatibilidade
        pass

    async def disconnect(self):
        if self.client:
            self.client.close()
            print("Desconectado do MongoDB.")

    def _to_objectid(self, id_value: Union[str, ObjectId, None]) -> Optional[ObjectId]:
        """
        Converte uma string para ObjectId quando apropriado. Se já for ObjectId, retorna como está.
        Retorna None se id_value for None.
        Levanta RepositoryError se a conversão falhar.
        """
        if id_value is None:
            return None
        if isinstance(id_value, ObjectId):
            return id_value
        try:
            return ObjectId(str(id_value))
        except Exception as e:
            raise RepositoryError(f"Identificador inválido para conversão em ObjectId: {e}")

    # Métodos para Character
    async def save_character(self, character: Character) -> str:
        if self.characters_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de personagens não estabelecida.")
        try:
            # Serializa o personagem garantindo que o campo _id seja um ObjectId
            character_dict = character.to_dict()
            # Normaliza id do personagem para ObjectId (aceita str ou ObjectId)
            char_obj_id = self._to_objectid(getattr(character, "id", None))
            if char_obj_id is not None:
                character_dict["_id"] = char_obj_id
            # Remove eventualmente uma chave antiga 'id' para evitar inconsistência
            if "id" in character_dict:
                character_dict.pop("id")
            result = await self.characters_collection.insert_one(character_dict)
            if not result.acknowledged:
                raise RepositoryError("Falha ao salvar personagem: operação não reconhecida.")
            return str(result.inserted_id)
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao salvar personagem: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao salvar personagem: {e}")

    async def get_character(self, character_id: str) -> Optional[Character]:
        print(f"[DEBUG] Entering get_character with identifier: {character_id}")
        if self.characters_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de personagens não estabelecida.")
        try:
            # Aceita tanto string quanto ObjectId como entrada
            obj_id = self._to_objectid(character_id)
            if obj_id is None:
                return None
            data = await self.characters_collection.find_one({"_id": obj_id})
            if data:
                return Character.from_dict(data)
            return None
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar personagem: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar personagem: {e}")

    async def get_character_by_id(self, character_id: ObjectId) -> Optional[Character]:
        if self.characters_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de personagens não estabelecida.")
        try:
            data = await self.characters_collection.find_one({"_id": character_id})
            if data:
                return Character.from_dict(data)
            return None
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar personagem por ID: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar personagem por ID: {e}")

    async def get_character_by_name_or_alias(self, name_or_alias: str) -> Optional[Character]:
        if self.characters_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de personagens não estabelecida.")
        try:
            # Case-insensitive search for name or alias
            data = await self.characters_collection.find_one({
                "$or": [
                    {"name": {"$regex": f"^{re.escape(name_or_alias)}$", "$options": "i"}},
                    {"alias": {"$regex": f"^{re.escape(name_or_alias)}$", "$options": "i"}}
                ]
            })
            print(f"[DEBUG] get_character_by_name_or_alias - Data retrieved: {data}")
            if data:
                return Character.from_dict(data)
            return None
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar personagem por nome/apelido: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar personagem por nome/apelido: {e}")

    async def get_character_by_id_or_name(self, identifier: str) -> Optional[Character]:
        """
        Tenta buscar um personagem por _id (quando `identifier` é um ObjectId ou hex de 24 chars)
        ou por nome/apelido caso contrário.
        """
        if self.characters_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de personagens não estabelecida.")
        # Se identifier for um ObjectId já, ou uma string hex de 24 chars, trata como id
        try:
            if isinstance(identifier, ObjectId) or (isinstance(identifier, str) and re.fullmatch(r'^[0-9a-fA-F]{24}$', identifier)):
                return await self.get_character(str(identifier))
            # Caso contrário, trata como nome ou apelido
            return await self.get_character_by_name_or_alias(identifier)
        except RepositoryError:
            # Repropaga erros de repositório
            raise
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar personagem: {e}")

    async def update_character(self, character: Character) -> bool:
        if self.characters_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de personagens não estabelecida.")
        try:
            character_dict = character.to_dict()
            # Normaliza o id usado no filtro para ObjectId
            filter_id = self._to_objectid(getattr(character, "id", None))
            if filter_id is None:
                raise RepositoryError("Identificador do personagem ausente para atualização.")
            # Garante que o documento de substituição contenha o mesmo _id em tipo ObjectId
            character_dict["_id"] = filter_id
            # Remove possível chave 'id' para evitar campos inconsistentes
            if "id" in character_dict:
                character_dict.pop("id")
            result = await self.characters_collection.replace_one({"_id": filter_id}, character_dict)
            if not result.acknowledged:
                raise RepositoryError("Falha ao atualizar personagem: operação não reconhecida.")
            return result.modified_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao atualizar personagem: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao atualizar personagem: {e}")

    async def delete_character(self, character_id: str) -> bool:
        if self.characters_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de personagens não estabelecida.")
        try:
            result = await self.characters_collection.delete_one({"_id": ObjectId(character_id)})
            if not result.acknowledged:
                raise RepositoryError("Falha ao deletar personagem: operação não reconhecida.")
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao deletar personagem: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao deletar personagem: {e}")

    async def get_all_characters(self) -> List[Character]:
        if self.characters_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de personagens não estabelecida.")
        try:
            characters = []
            # Usar to_list(None) para obter todos os documentos de forma assíncrona
            data_list = await self.characters_collection.find().to_list(None)
            for data in data_list:
                characters.append(Character.from_dict(data))
            return characters
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar todos os personagens: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar todos os personagens: {e}")

    async def delete_all_characters(self) -> int:
        if self.characters_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de personagens não estabelecida.")
        try:
            result = await self.characters_collection.delete_many({})
            if not result.acknowledged:
                raise RepositoryError("Falha ao deletar todos os personagens: operação não reconhecida.")
            return result.deleted_count
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao deletar todos os personagens: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao deletar todos os personagens: {e}")

    # Métodos para ClassTemplate
    async def save_class_template(self, class_template: ClassTemplate) -> str:
        if self.classes_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de classes não estabelecida.")
        try:
            class_template_dict = class_template.to_dict() # Usar to_dict para serialização
            class_template_dict["_id"] = class_template_dict.pop("id") # Renomeia 'id' para '_id'
            result = await self.classes_collection.insert_one(class_template_dict)
            if not result.acknowledged:
                raise RepositoryError("Falha ao salvar template de classe: operação não reconhecida.")
            return str(result.inserted_id)
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao salvar template de classe: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao salvar template de classe: {e}")

    async def get_class_template(self, class_name: str) -> Optional[ClassTemplate]:
        if self.classes_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de classes não estabelecida.")
        try:
            data = await self.classes_collection.find_one({"name": class_name})
            if data:
                return ClassTemplate.from_dict(data) # Usar from_dict para desserialização
            return None
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar template de classe: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar template de classe: {e}")

    async def update_class_template(self, class_template: ClassTemplate) -> bool:
        if self.classes_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de classes não estabelecida.")
        try:
            class_template_dict = class_template.to_dict() # Usar to_dict para serialização
            result = await self.classes_collection.replace_one({"_id": class_template.id}, class_template_dict)
            if not result.acknowledged:
                raise RepositoryError("Falha ao atualizar template de classe: operação não reconhecida.")
            return result.modified_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao atualizar template de classe: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao atualizar template de classe: {e}")

    async def delete_class_template(self, class_name: str) -> bool:
        if self.classes_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de classes não estabelecida.")
        try:
            result = await self.classes_collection.delete_one({"_id": ObjectId(class_name)})
            if not result.acknowledged:
                raise RepositoryError("Falha ao deletar template de classe: operação não reconhecida.")
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao deletar template de classe: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao deletar template de classe: {e}")

    # Métodos para PlayerPreferences
    async def save_player_preferences(self, preferences: PlayerPreferences) -> str:
        if self.player_preferences_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de preferências do jogador não estabelecida.")
        try:
            preferences_dict = preferences.__dict__
            result = await self.player_preferences_collection.insert_one(preferences_dict)
            if not result.acknowledged:
                raise RepositoryError("Falha ao salvar preferências do jogador: operação não reconhecida.")
            return str(result.inserted_id)
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao salvar preferências do jogador: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao salvar preferências do jogador: {e}")

    async def get_player_preferences(self, player_discord_id: str) -> Optional[PlayerPreferences]:
        if self.player_preferences_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de preferências do jogador não estabelecida.")
        try:
            data = await self.player_preferences_collection.find_one({"player_discord_id": player_discord_id})
            if data:
                return PlayerPreferences(**data)
            return None
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar preferências do jogador: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar preferências do jogador: {e}")

    async def update_player_preferences(self, preferences: PlayerPreferences) -> bool:
        if self.player_preferences_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de preferências do jogador não estabelecida.")
        try:
            preferences_dict = preferences.__dict__
            result = await self.player_preferences_collection.replace_one({"player_discord_id": preferences.player_discord_id}, preferences_dict)
            if not result.acknowledged:
                raise RepositoryError("Falha ao atualizar preferências do jogador: operação não reconhecida.")
            return result.modified_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao atualizar preferências do jogador: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao atualizar preferências do jogador: {e}")

    async def delete_player_preferences(self, player_discord_id: str) -> bool:
        if self.player_preferences_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de preferências do jogador não estabelecida.")
        try:
            result = await self.player_preferences_collection.delete_one({"player_discord_id": player_discord_id})
            if not result.acknowledged:
                raise RepositoryError("Falha ao deletar preferências do jogador: operação não reconhecida.")
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao deletar preferências do jogador: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao deletar preferências do jogador: {e}")

    # Métodos para Transformation
    async def save_transformation(self, transformation: Transformation) -> str:
        if self.transformacoes_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de transformações não estabelecida.")
        try:
            transformation_dict = transformation.__dict__
            result = await self.transformacoes_collection.insert_one(transformation_dict)
            if not result.acknowledged:
                raise RepositoryError("Falha ao salvar transformação: operação não reconhecida.")
            return str(result.inserted_id)
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao salvar transformação: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao salvar transformação: {e}")

    async def get_transformation(self, transformation_id: str) -> Optional[Transformation]:
        if self.transformacoes_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de transformações não estabelecida.")
        try:
            data = await self.transformacoes_collection.find_one({"id": transformation_id})
            if data:
                return Transformation(**data)
            return None
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar transformação: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar transformação: {e}")

    async def update_transformation(self, transformation: Transformation) -> bool:
        if self.transformacoes_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de transformações não estabelecida.")
        try:
            transformation_dict = transformation.__dict__
            result = await self.transformacoes_collection.replace_one({"id": transformation.id}, transformation_dict)
            if not result.acknowledged:
                raise RepositoryError("Falha ao atualizar transformação: operação não reconhecida.")
            return result.modified_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao atualizar transformação: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao atualizar transformação: {e}")

    async def delete_transformation(self, transformation_id: str) -> bool:
        if self.transformacoes_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de transformações não estabelecida.")
        try:
            result = await self.transformacoes_collection.delete_one({"id": transformation_id})
            if not result.acknowledged:
                raise RepositoryError("Falha ao deletar transformação: operação não reconhecida.")
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao deletar transformação: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao deletar transformação: {e}")

    # Métodos para Titulos (estrutura simples)
    async def save_titulo(self, titulo_id: str, titulo_data: Dict[str, Any]) -> str:
        if self.titulos_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de títulos não estabelecida.")
        try:
            # Garante que o ID seja usado como _id no MongoDB
            titulo_data["_id"] = titulo_id
            result = await self.titulos_collection.insert_one(titulo_data)
            if not result.acknowledged:
                raise RepositoryError("Falha ao salvar título: operação não reconhecida.")
            return str(result.inserted_id)
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao salvar título: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao salvar título: {e}")

    async def get_titulo(self, titulo_id: str) -> Optional[Dict[str, Any]]:
        if self.titulos_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de títulos não estabelecida.")
        try:
            data = await self.titulos_collection.find_one({"_id": titulo_id})
            return data
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao buscar título: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao buscar título: {e}")

    async def update_titulo(self, titulo_id: str, titulo_data: Dict[str, Any]) -> bool:
        if self.titulos_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de títulos não estabelecida.")
        try:
            result = await self.titulos_collection.replace_one({"_id": titulo_id}, titulo_data)
            if not result.acknowledged:
                raise RepositoryError("Falha ao atualizar título: operação não reconhecida.")
            return result.modified_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao atualizar título: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao atualizar título: {e}")

    async def delete_titulo(self, titulo_id: str) -> bool:
        if self.titulos_collection is None:
            raise DatabaseConnectionError("Conexão com a coleção de títulos não estabelecida.")
        try:
            result = await self.titulos_collection.delete_one({"_id": titulo_id})
            if not result.acknowledged:
                raise RepositoryError("Falha ao deletar título: operação não reconhecida.")
            return result.deleted_count > 0
        except PyMongoError as e:
            raise RepositoryError(f"Erro no banco de dados ao deletar título: {e}")
        except Exception as e:
            raise RepositoryError(f"Erro inesperado ao deletar título: {e}")

