import os
import logging
from datetime import datetime, timedelta
from src.utils.helpers.datetime_utils import safe_parse_datetime
from src.infrastructure.cache.redis_repository import RedisRepository
from src.utils.exceptions.infrastructure_exceptions import DatabaseConnectionError, CacheError

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def cleanup_expired_combat_sessions(redis_repo: RedisRepository):
    """
    Limpa sessões de combate expiradas do Redis.
    """
    logging.info("Iniciando limpeza de sessões de combate expiradas...")
    try:
        all_sessions = await redis_repo.get_all_combat_sessions()
        current_time = datetime.utcnow()
        
        cleaned_count = 0
        for session in all_sessions:
            expires_at_dt = safe_parse_datetime(session.expires_at) or datetime.utcnow()
            if expires_at_dt <= current_time:
                await redis_repo.delete_combat_session(session.id)
                cleaned_count += 1
                logging.info(f"Sessão de combate expirada '{session.id}' limpa.")
        
        logging.info(f"Limpeza de sessões de combate concluída. {cleaned_count} sessões expiradas foram removidas.")
    except DatabaseConnectionError as e:
        logging.error(f"Erro de conexão com o Redis durante a limpeza: {e}")
        raise
    except CacheError as e:
        logging.error(f"Erro no cache Redis durante a limpeza: {e}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado durante a limpeza de sessões de combate: {e}")
        raise

if __name__ == "__main__":
    # Instantiate RedisRepository
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_db = int(os.getenv("REDIS_DB", 0))

    try:
        redis_repository = RedisRepository(host=redis_host, port=redis_port, db=redis_db)
        await cleanup_expired_combat_sessions(redis_repository)
        await redis_repository.disconnect() # Adicionar desconexão explícita
    except Exception as e:
        logging.critical(f"Falha crítica ao executar o script de limpeza de sessões: {e}")