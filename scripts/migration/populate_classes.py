import os
import pymongo
from pymongo.errors import ConnectionFailure # Import ConnectionFailure directly
from datetime import datetime
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")
MONGODB_DATABASE_NAME = os.environ.get("MONGODB_DATABASE_NAME")

# Define the classes for the RPG Bot
classes_data = [
    {
        "nome": "Bárbaro",
        "descricao": "Extremamente fortes e resistentes, especialistas em combate bruto.",
        "atributos_base": {"forca": 35, "destreza": 15, "constituicao": 20, "inteligencia": 5, "sabedoria": 5, "carisma": 10},
        "hp_formula": "30d3",
        "chakra_formula": "5d5",
        "fp_formula": "15d5",
        "habilidades_iniciais": []
    },
    {
        "nome": "Pugilista",
        "descricao": "Voltados ao combate corpo-a-corpo, ágeis e precisos.",
        "atributos_base": {"forca": 25, "destreza": 30, "constituicao": 15, "inteligencia": 7, "sabedoria": 7, "carisma": 6},
        "hp_formula": "21d3",
        "chakra_formula": "8d5",
        "fp_formula": "11d5",
        "habilidades_iniciais": []
    },
    {
        "nome": "Encouraçado",
        "descricao": "Focados na capacidade de aguentar golpes e proteger aliados.",
        "atributos_base": {"forca": 20, "destreza": 10, "constituicao": 40, "inteligencia": 3, "sabedoria": 2, "carisma": 15},
        "hp_formula": "45d3",
        "chakra_formula": "5d5",
        "fp_formula": "5d5",
        "habilidades_iniciais": []
    },
    {
        "nome": "Desgarrado",
        "descricao": "Voltado a várias especializações diferentes, equilibrado em tudo.",
        "atributos_base": {"forca": 15, "destreza": 15, "constituicao": 15, "inteligencia": 15, "sabedoria": 15, "carisma": 15},
        "hp_formula": "15d5",
        "chakra_formula": "15d5",
        "fp_formula": "15d5",
        "habilidades_iniciais": []
    },
    {
        "nome": "Mago",
        "descricao": "Portadores de gigantescas reservas de chakra, mestres das artes místicas.",
        "atributos_base": {"forca": 3, "destreza": 15, "constituicao": 2, "inteligencia": 50, "sabedoria": 10, "carisma": 10},
        "hp_formula": "10d4",
        "chakra_formula": "40d4",
        "fp_formula": "15d5",
        "habilidades_iniciais": []
    },
    {
        "nome": "Curandeiro",
        "descricao": "Voltados para habilidades suplementares, cura e suporte.",
        "atributos_base": {"forca": 5, "destreza": 15, "constituicao": 15, "inteligencia": 40, "sabedoria": 10, "carisma": 5},
        "hp_formula": "20d3",
        "chakra_formula": "30d4",
        "fp_formula": "10d5",
        "habilidades_iniciais": []
    }
]

def populate_classes():
    if not MONGODB_CONNECTION_STRING or not MONGODB_DATABASE_NAME:
        print("Erro: Variáveis de ambiente MONGODB_CONNECTION_STRING e MONGODB_DATABASE_NAME devem ser definidas.")
        return

    client = None # Initialize client to None
    try:
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        classes_collection = db.classes

        print(f"Conectado ao MongoDB. Banco de dados: {MONGODB_DATABASE_NAME}")

        inserted_count = 0
        skipped_count = 0

        for class_data in classes_data:
            class_name = class_data["nome"]
            existing_class = classes_collection.find_one({"nome": class_name})

            if existing_class:
                print(f"Classe '{class_name}' já existe. Pulando inserção.")
                skipped_count += 1
            else:
                now = datetime.utcnow()
                class_data["created_at"] = now
                class_data["updated_at"] = now
                insert_result = classes_collection.insert_one(class_data)
                print(f"Classe '{class_name}' inserida com sucesso. ID: {insert_result.inserted_id}")
                inserted_count += 1

        print(f"\nProcesso de população concluído.")
        print(f"Classes inseridas: {inserted_count}")
        print(f"Classes puladas (já existentes): {skipped_count}")

    except ConnectionFailure as e: # Use the directly imported ConnectionFailure
        print(f"Erro de conexão com o MongoDB: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        if client:
            client.close()
            print("Conexão com o MongoDB fechada.")

if __name__ == "__main__":
    populate_classes()