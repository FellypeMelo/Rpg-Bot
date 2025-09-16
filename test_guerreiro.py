from src.core.services.character_service import CharacterService
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from config.settings.base_settings import BaseSettings

# Load settings
settings = BaseSettings()

# Create a repository with test database
repo = MongoDBRepository(
    connection_string=settings.MONGODB_CONNECTION_STRING,
    database_name=settings.MONGODB_DATABASE_NAME,
    collection_name=settings.MONGODB_CHARACTER_COLLECTION
)

# Create character service
character_service = CharacterService(repo)

# Test creating a character with Guerreiro class
try:
    character = character_service.create_character(
        name="Meu Herói", 
        class_name="Guerreiro", 
        alias="O Bravo"
    )
    print(f"Character created successfully: {character.name}, Class: {character.class_name}, Alias: {character.alias}")
    print(f"Attributes: {character.attributes}")
    print(f"HP: {character.hp}, Chakra: {character.chakra}, FP: {character.fp}")
except Exception as e:
    print(f"Error creating character: {e}")
finally:
    # Close the database connection
    repo.disconnect()