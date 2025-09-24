import asyncio, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from dotenv import load_dotenv
load_dotenv()
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.class_repository import ClassRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.core.services.character_service import CharacterService

async def main():
    repo = MongoDBRepository(os.getenv('MONGODB_CONNECTION_STRING','mongodb://localhost:27017/'), os.getenv('MONGODB_DATABASE_NAME','rpg_bot_db'))
    await repo.connect()
    try:
        char_service = CharacterService(repo, TransformationRepository(repo), ClassRepository(repo))
        c = await char_service.get_character('Renee')
        print('Before masteries:', c.masteries)
        # simulate maestria spend
        c.pontos.setdefault('mastery', {'total':0,'gasto':0})
        c.pontos['mastery']['total'] = c.pontos['mastery'].get('total',0) + 200
        # spend 100
        c.pontos['mastery']['total'] -= 100
        c.pontos['mastery']['gasto'] = c.pontos['mastery'].get('gasto',0) + 100
        c.masteries = c.masteries or {}
        c.masteries['Estilo Fogo'] = c.masteries.get('Estilo Fogo',0) + 100
        await repo.update_character(c)
        re = await char_service.get_character('Renee')
        print('After masteries:', re.masteries)
        print('Pontos maestria:', re.pontos.get('mastery'))
        # simulate PH spend
        re.pontos.setdefault('ph', {'total':0,'gasto':[]})
        re.pontos['ph']['total'] += 5
        re.pontos['ph']['total'] -= 1
        re.pontos['ph']['gasto'].append({'descricao':'bomba','custo':1,'data':None})
        await repo.update_character(re)
        final = await char_service.get_character('Renee')
        print('PH gasto:', final.pontos['ph']['gasto'])
    finally:
        await repo.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
