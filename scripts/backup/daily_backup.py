import os
import subprocess
import datetime
import logging

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_mongodb_backup(
    db_name: str,
    backup_dir: str,
    mongo_uri: str = "mongodb://localhost:27017/"
):
    """
    Executa um backup do MongoDB usando mongodump.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(backup_dir, f"{db_name}_backup_{timestamp}")

    # Ensure backup directory exists
    os.makedirs(output_path, exist_ok=True)

    command = [
        "mongodump",
        f"--uri={mongo_uri}",
        f"--db={db_name}",
        f"--out={output_path}"
    ]

    logging.info(f"Iniciando backup do MongoDB para o banco de dados '{db_name}' em '{output_path}'...")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logging.info(f"Backup do MongoDB concluído com sucesso para '{db_name}'.")
        logging.debug(f"Saída do mongodump:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao executar backup do MongoDB para '{db_name}': {e}")
        logging.error(f"Stderr:\n{e.stderr}")
        raise
    except FileNotFoundError:
        logging.error("Comando 'mongodump' não encontrado. Certifique-se de que o MongoDB está instalado e 'mongodump' está no PATH.")
        raise

def run_redis_backup(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    backup_dir: str = "redis_backups"
):
    """
    Executa um backup do Redis usando o comando BGSAVE.
    Isso salva o estado atual do Redis em um arquivo RDB.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(backup_dir, f"redis_dump_{timestamp}.rdb")

    os.makedirs(backup_dir, exist_ok=True)

    # Connect to Redis and execute BGSAVE
    try:
        import redis
        r = redis.Redis(host=redis_host, port=redis_port)
        r.bgsave()
        logging.info(f"Comando BGSAVE do Redis executado com sucesso. O arquivo RDB será salvo no diretório de trabalho do Redis.")
        logging.warning(f"Para mover o arquivo RDB para '{output_file}', você precisará configurá-lo no redis.conf ou movê-lo manualmente.")
    except ImportError:
        logging.error("A biblioteca 'redis' não está instalada. Por favor, instale-a com 'pip install redis'.")
        raise
    except redis.ConnectionError as e:
        logging.error(f"Erro de conexão com o Redis em {redis_host}:{redis_port}: {e}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado ao executar backup do Redis: {e}")
        raise

if __name__ == "__main__":
    # Example usage:
    # Ensure you have mongodump and redis-cli in your PATH or provide full paths
    
    # MongoDB Backup
    mongo_db_name = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")
    mongo_backup_dir = "backups/mongodb"
    mongo_connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")

    try:
        run_mongodb_backup(mongo_db_name, mongo_backup_dir, mongo_connection_string)
    except Exception as e:
        logging.error(f"Falha no backup do MongoDB: {e}")

    # Redis Backup
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_backup_dir = "backups/redis"

    try:
        run_redis_backup(redis_host, redis_port, redis_backup_dir)
    except Exception as e:
        logging.error(f"Falha no backup do Redis: {e}")