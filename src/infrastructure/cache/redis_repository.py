import redis
import json
from datetime import timedelta
from typing import Dict, Optional, List, cast
from datetime import timedelta
from src.core.entities.combat_session import CombatSession
from src.utils.exceptions.infrastructure_exceptions import CacheError, DatabaseConnectionError

class RedisRepository:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, decode_responses: bool = True):
        self.host = host
        self.port = port
        self.db = db
        self.decode_responses = decode_responses
        self.client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self):
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=self.decode_responses
            )
            self.client.ping() # Test connection
            print(f"Conectado ao Redis: {self.host}:{self.port}/{self.db}")
        except redis.ConnectionError as e:
            raise DatabaseConnectionError(f"Falha ao conectar ao Redis: {e}")
        except Exception as e:
            raise DatabaseConnectionError(f"Erro inesperado ao conectar ao Redis: {e}")

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Desconectado do Redis.")

    def save_combat_session(self, session: CombatSession, ttl_seconds: int) -> bool:
        if not self.client:
            raise CacheError("Cliente Redis não está conectado.")
        try:
            session_dict = session.to_dict()
            # Redis stores strings, so convert dict to JSON string
            result = self.client.setex(f"combat_session:{session.id}", ttl_seconds, json.dumps(session_dict))
            return bool(result)
        except redis.RedisError as e:
            raise CacheError(f"Erro no Redis ao salvar sessão de combate: {e}")
        except Exception as e:
            raise CacheError(f"Erro inesperado ao salvar sessão de combate: {e}")

    def get_combat_session(self, session_id: str) -> Optional[CombatSession]:
        if not self.client:
            raise CacheError("Cliente Redis não está conectado.")
        try:
            data = self.client.get(f"combat_session:{session_id}")
            if data:
                # Handle both string and bytes data types
                if isinstance(data, bytes):
                    data_str = data.decode('utf-8')
                else:
                    data_str = str(data)
                # Convert JSON string back to dict and then to CombatSession object
                return CombatSession.from_dict(json.loads(data_str))
            return None
        except redis.RedisError as e:
            raise CacheError(f"Erro no Redis ao buscar sessão de combate: {e}")
        except Exception as e:
            raise CacheError(f"Erro inesperado ao buscar sessão de combate: {e}")

    def update_combat_session(self, session: CombatSession) -> bool:
        if not self.client:
            raise CacheError("Cliente Redis não está conectado.")
        try:
            # Get current TTL to preserve it, or set a default if none exists
            ttl_value = cast(int, self.client.ttl(f"combat_session:{session.id}"))
            
            if ttl_value == -2:  # Key does not exist
                return False
            elif ttl_value == -1:  # Key exists but has no expire, set to default 4 hours
                ttl_seconds = int(timedelta(hours=4).total_seconds())
            else:
                ttl_seconds = ttl_value
            
            session_dict = session.to_dict()
            result = self.client.setex(f"combat_session:{session.id}", ttl_seconds, json.dumps(session_dict))
            return bool(result)
        except redis.RedisError as e:
            raise CacheError(f"Erro no Redis ao atualizar sessão de combate: {e}")
        except Exception as e:
            raise CacheError(f"Erro inesperado ao atualizar sessão de combate: {e}")

    def delete_combat_session(self, session_id: str) -> bool:
        if not self.client:
            raise CacheError("Cliente Redis não está conectado.")
        try:
            result = self.client.delete(f"combat_session:{session_id}")
            return bool(result)
        except redis.RedisError as e:
            raise CacheError(f"Erro no Redis ao deletar sessão de combate: {e}")
        except Exception as e:
            raise CacheError(f"Erro inesperado ao deletar sessão de combate: {e}")

    def get_all_combat_sessions(self) -> List[CombatSession]:
        if not self.client:
            raise CacheError("Cliente Redis não está conectado.")
        try:
            sessions = []
            # Scan for keys matching the pattern
            for key in self.client.scan_iter("combat_session:*"):
                data = self.client.get(key)
                if data:
                    # Handle both string and bytes data types
                    if isinstance(data, bytes):
                        data_str = data.decode('utf-8')
                    else:
                        data_str = str(data)
                    sessions.append(CombatSession.from_dict(json.loads(data_str)))
            return sessions
        except redis.RedisError as e:
            raise CacheError(f"Erro no Redis ao buscar todas as sessões de combate: {e}")
        except Exception as e:
            raise CacheError(f"Erro inesperado ao buscar todas as sessões de combate: {e}")