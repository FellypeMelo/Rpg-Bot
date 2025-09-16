import os
import logging
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.utils.exceptions.infrastructure_exceptions import DatabaseConnectionError, RepositoryError

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_mongodb_maintenance(mongo_repo: MongoDBRepository):
    """
    Executa tarefas de manutenção no MongoDB, como otimização de índices.
    """
    logging.info("Iniciando manutenção do MongoDB...")
    try:
        # Example: Ensure indexes are optimized (MongoDB handles this largely automatically,
        # but explicit calls can be made if needed for specific scenarios).
        # For this project, we'll ensure the 'id' field is indexed for efficient lookups.
        
        # Ensure 'id' field is indexed for characters collection
        if mongo_repo.collection is not None:
            mongo_repo.collection.create_index("id", unique=True)
            logging.info("Índice 'id' criado/verificado na coleção de personagens.")
        else:
            logging.warning("Repositório MongoDB não conectado. Não foi possível verificar/criar índices.")

        # Other maintenance tasks could include:
        # - Compacting collections (use with caution, can be resource intensive)
        # - Analyzing collection statistics
        # - Dropping old/unused collections (e.g., old audit logs)

        logging.info("Manutenção do MongoDB concluída.")
    except DatabaseConnectionError as e:
        logging.error(f"Erro de conexão com o MongoDB durante a manutenção: {e}")
        raise
    except RepositoryError as e:
        logging.error(f"Erro no repositório MongoDB durante a manutenção: {e}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado durante a manutenção do MongoDB: {e}")
        raise

if __name__ == "__main__":
    # Instantiate MongoDBRepository
    mongo_connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    mongo_database_name = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")
    mongo_collection_name = os.getenv("MONGODB_CHARACTER_COLLECTION", "characters")

    try:
        mongo_repository = MongoDBRepository(
            connection_string=mongo_connection_string,
            database_name=mongo_database_name,
            collection_name=mongo_collection_name
        )
        run_mongodb_maintenance(mongo_repository)
    except Exception as e:
        logging.critical(f"Falha crítica ao executar o script de manutenção do banco de dados: {e}")