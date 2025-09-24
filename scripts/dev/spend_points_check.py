import asyncio
import os
import sys
from dotenv import load_dotenv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

load_dotenv()
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.class_repository import ClassRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.core.services.character_service import CharacterService

MONGO_URI = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
MONGO_DB = os.getenv('MONGODB_DATABASE_NAME', 'rpg_bot_db')

async def main(name_or_id: str, attr: str, amount: int):
    repo = MongoDBRepository(MONGO_URI, MONGO_DB)
    await repo.connect()
    try:
        class_repo = ClassRepository(repo)
        trans_repo = TransformationRepository(repo)
        char_service = CharacterService(repo, trans_repo, class_repo)

        c = await char_service.get_character(name_or_id)
        if not c:
            print('Character not found')
            return
        print('Before:')
        print('attributes:', c.attributes)
        print('modifiers:', c.modifiers)
        print('pontos:', c.pontos)

        # apply attribute increase
        new_attrs = c.attributes.copy()
        new_attrs[attr] = new_attrs.get(attr, 0) + amount

        # reduce pontos (simulate)
        new_pontos = c.pontos.copy()
        new_pontos.setdefault('status', {'total':0,'gasto':0})
        new_pontos['status']['total'] = new_pontos['status'].get('total',0) - amount
        new_pontos['status']['gasto'] = new_pontos['status'].get('gasto',0) + amount

        await char_service.update_character(str(c.id), 'attributes', new_attrs)
        await char_service.update_character(str(c.id), 'pontos', new_pontos)

        reloaded = await char_service.get_character(str(c.id))
        print('\nAfter:')
        print('attributes:', reloaded.attributes)
        print('modifiers:', reloaded.modifiers)
        print('pontos:', reloaded.pontos)
    finally:
        await repo.disconnect()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print('Usage: python spend_points_check.py <name_or_id> <attr> <amount>')
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3])))
