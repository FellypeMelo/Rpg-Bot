import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure project root is on sys.path so `src` package can be imported when running as a script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.class_repository import ClassRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.core.services.character_service import CharacterService
from src.core.services.levelup_service import LevelUpService

load_dotenv()

MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")


async def main(identifier_or_name: str):
    repo = MongoDBRepository(MONGO_URI, MONGO_DB)
    await repo.connect()
    try:
        class_repo = ClassRepository(repo)
        trans_repo = TransformationRepository(repo)
        char_service = CharacterService(repo, trans_repo, class_repo)
        levelup_service = LevelUpService(char_service, class_repo)

        print(f"Looking up character '{identifier_or_name}'...")
        character = await char_service.get_character(identifier_or_name)
        if not character:
            print("Character not found. Exiting.")
            return
        print(f"Before levelup: name={character.name}, level={character.level}, id={getattr(character, 'id', None)}")

        # Perform one level up
        updated = await levelup_service.level_up_character(character, 1)
        print(f"Levelup executed in memory. New level (in returned obj): {updated.level}")

        # Reload from DB
        identifier = str(getattr(character, 'id', getattr(character, '_id', None)))
        reloaded = await repo.get_character_by_id_or_name(identifier)
        if reloaded:
            print(f"Reloaded from DB: name={reloaded.name}, level={reloaded.level}, id={getattr(reloaded, 'id', None)}")
        else:
            print("Reloaded character not found in DB after update.")
    finally:
        await repo.disconnect()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python levelup_check.py <character_id_or_name>')
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
