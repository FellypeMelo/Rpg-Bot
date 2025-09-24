import json
import redis.asyncio as redis
from typing import Optional, Dict, Any, List
from src.core.entities.combat_session import CombatSession
from src.utils.exceptions.infrastructure_exceptions import CacheError

class RedisRepository:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        if not self.redis_client:
            # decode_responses=True garante que os valores retornados já são strings
            self.redis_client = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
            try:
                await self.redis_client.ping()
                # print(f"Conectado ao Redis em {self.host}:{self.port}/{self.db}") # Removido para evitar logs excessivos
            except redis.ConnectionError as e:
                raise CacheError(f"Falha ao conectar ao Redis: {e}")

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def save_combat_session(self, session: CombatSession, ttl_seconds: int = 3600):
        if not self.redis_client:
            raise CacheError("Redis client not connected.")
        session_json = json.dumps(session.to_dict())
        await self.redis_client.set(f"combat_session:{session.id}", session_json, ex=ttl_seconds)
        # Mapeia o ID do canal para o ID da sessão ativa
        await self.redis_client.set(f"combat_session:channel:{session.channel_id}", str(session.id), ex=ttl_seconds)

    async def get_combat_session(self, session_id: str) -> Optional[CombatSession]:
        if not self.redis_client:
            raise CacheError("Redis client not connected.")
        session_data = await self.redis_client.get(f"combat_session:{session_id}")
        if session_data:
            # session_data já é uma string devido a decode_responses=True
            return CombatSession.from_dict(json.loads(session_data))
        return None

    async def update_combat_session(self, session: CombatSession):
        if not self.redis_client:
            raise CacheError("Redis client not connected.")
        session_json = json.dumps(session.to_dict())
        # Preserva o TTL se existir, caso contrário, define um padrão
        ttl = await self.redis_client.ttl(f"combat_session:{session.id}")
        if ttl == -1: # Sem expiração
            await self.redis_client.set(f"combat_session:{session.id}", session_json)
            await self.redis_client.set(f"combat_session:channel:{session.channel_id}", str(session.id))
        else:
            await self.redis_client.set(f"combat_session:{session.id}", session_json, ex=ttl)
            await self.redis_client.set(f"combat_session:channel:{session.channel_id}", str(session.id), ex=ttl)

    async def delete_combat_session(self, session_id: str):
        if not self.redis_client:
            raise CacheError("Redis client not connected.")
        # Tenta obter o channel_id da sessão antes de deletar o mapeamento
        session_data = await self.redis_client.get(f"combat_session:{session_id}")
        if session_data:
            try:
                session = CombatSession.from_dict(json.loads(session_data))
                await self.redis_client.delete(f"combat_session:channel:{session.channel_id}")
            except Exception as e:
                # Logar o erro, mas não impedir a exclusão da sessão principal
                print(f"Erro ao tentar deletar mapeamento de canal para sessão {session_id}: {e}")
        await self.redis_client.delete(f"combat_session:{session.id}")

    async def get_combat_session_by_channel(self, channel_id: str) -> Optional[CombatSession]:
        """
        Recupera uma sessão de combate do Redis usando o ID do canal.
        """
        if not self.redis_client:
            raise CacheError("Redis client not connected.")
        session_key = f"combat_session:channel:{channel_id}"
        session_id = await self.redis_client.get(session_key)
        if session_id:
            # session_id já é uma string (devido a decode_responses=True), não precisa de decode
            session_data = await self.redis_client.get(f"combat_session:{session_id}")
            if session_data:
                # session_data já é uma string, não precisa de decode
                return CombatSession.from_dict(json.loads(session_data))
        return None

    async def get_all_combat_sessions(self) -> List[CombatSession]:
        """
        Recupera todas as sessões de combate ativas.
        """
        if not self.redis_client:
            raise CacheError("Redis client not connected.")
        session_keys = await self.redis_client.keys("combat_session:*")
        sessions: List[CombatSession] = []
        for key in session_keys:
            # Ignorar chaves de mapeamento de canal
            if "combat_session:channel:" in key:
                continue
            session_data = await self.redis_client.get(key)
            if session_data:
                sessions.append(CombatSession.from_dict(json.loads(session_data)))
        return sessions