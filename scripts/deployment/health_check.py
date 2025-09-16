import requests
import sys
import os
import logging

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_discord_bot_status(bot_token: str) -> bool:
    """
    Verifica o status do bot Discord fazendo uma requisição à API do Discord.
    Isso é um check básico para ver se o token é válido e se o bot pode se conectar.
    """
    headers = {
        "Authorization": f"Bot {bot_token}"
    }
    # A requisição a /users/@me é um endpoint leve para verificar a autenticação
    url = "https://discord.com/api/v10/users/@me"
    
    logging.info("Verificando status do bot Discord...")
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        user_data = response.json()
        logging.info(f"Bot Discord conectado como: {user_data['username']}#{user_data['discriminator']}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Falha ao conectar ao Discord API: {e}")
        return False
    except Exception as e:
        logging.error(f"Erro inesperado ao verificar status do bot Discord: {e}")
        return False

def check_mongodb_status(mongo_uri: str = "mongodb://localhost:27017/") -> bool:
    """
    Verifica o status da conexão com o MongoDB.
    """
    try:
        from pymongo import MongoClient
        logging.info(f"Verificando status do MongoDB em {mongo_uri}...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        logging.info("Conexão com o MongoDB bem-sucedida.")
        client.close()
        return True
    except ImportError:
        logging.error("A biblioteca 'pymongo' não está instalada. Por favor, instale-a com 'pip install pymongo'.")
        return False
    except Exception as e:
        logging.error(f"Falha ao conectar ao MongoDB: {e}")
        return False

def check_redis_status(redis_host: str = "localhost", redis_port: int = 6379) -> bool:
    """
    Verifica o status da conexão com o Redis.
    """
    try:
        import redis
        logging.info(f"Verificando status do Redis em {redis_host}:{redis_port}...")
        client = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=5)
        client.ping()
        logging.info("Conexão com o Redis bem-sucedida.")
        client.close()
        return True
    except ImportError:
        logging.error("A biblioteca 'redis' não está instalada. Por favor, instale-a com 'pip install redis'.")
        return False
    except Exception as e:
        logging.error(f"Falha ao conectar ao Redis: {e}")
        return False

def main():
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        logging.error("Variável de ambiente DISCORD_TOKEN não definida.")
        sys.exit(1)

    mongo_uri = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    all_ok = True

    if not check_discord_bot_status(discord_token):
        all_ok = False
    
    if not check_mongodb_status(mongo_uri):
        all_ok = False

    if not check_redis_status(redis_host, redis_port):
        all_ok = False

    if all_ok:
        logging.info("Todos os serviços estão operacionais.")
        sys.exit(0)
    else:
        logging.error("Um ou mais serviços não estão operacionais.")
        sys.exit(1)

if __name__ == "__main__":
    # Add requests to requirements.txt if not already there
    # pip install requests
    main()