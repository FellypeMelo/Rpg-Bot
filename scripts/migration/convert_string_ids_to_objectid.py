"""
Script seguro para converter documentos no MongoDB que tenham `_id` armazenado como string
para `ObjectId` quando o valor é um hex válido.

Funcionalidades:
- Dry-run por padrão: apenas relata quantos documentos seriam convertidos.
- `--apply` para aplicar as mudanças.
- `--uri` e `--db` para configurar conexão.
- CUIDADO: operação destrutiva (cria novo documento com ObjectId e remove o antigo). Faça backup antes.

Uso:
    python convert_string_ids_to_objectid.py --uri "mongodb://localhost:27017" --db mydb --apply

"""
import argparse
import re
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio


HEX24 = re.compile(r"^[0-9a-fA-F]{24}$")


async def _find_string_id_docs(collection):
    # Busca documentos cujo _id seja string e com formato hex de 24 chars
    cursor = collection.find({"_id": {"$type": "string"}})
    matches = []
    async for doc in cursor:
        _id = doc.get("_id")
        if isinstance(_id, str) and HEX24.match(_id):
            matches.append(doc)
    return matches


async def convert_collection(collection, apply_changes=False):
    docs = await _find_string_id_docs(collection)
    if not docs:
        return 0, []
    converted = []
    for doc in docs:
        old_id = doc["_id"]
        new_id = ObjectId(old_id)
        # Remove old _id from doc dict and set new one
        new_doc = dict(doc)
        new_doc.pop("_id", None)
        new_doc["_id"] = new_id
        converted.append((old_id, new_id, new_doc))
    if apply_changes:
        for old_id, new_id, new_doc in converted:
            # Insert with new ObjectId and remove old
            await collection.insert_one(new_doc)
            await collection.delete_one({"_id": old_id})
    return len(converted), converted


async def main(args):
    client = AsyncIOMotorClient(args.uri)
    db = client[args.db]
    # Você pode limitar as coleções a serem verificadas; por padrão verifica `characters` e `classes`.
    target_collections = args.collections or ["characters"]
    total = 0
    details = {}
    for coll_name in target_collections:
        coll = db[coll_name]
        count, converted = await convert_collection(coll, apply_changes=args.apply)
        total += count
        details[coll_name] = converted
    if args.apply:
        print(f"Applied conversion: total documents converted: {total}")
    else:
        print(f"Dry-run: total documents that would be converted: {total}")
    # AsyncIOMotorClient.close() is synchronous (not awaitable)
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert string _id hex values to ObjectId in MongoDB collections")
    parser.add_argument("--uri", default="mongodb://localhost:27017", help="MongoDB connection URI")
    parser.add_argument("--db", required=True, help="Database name")
    parser.add_argument("--apply", action="store_true", help="Apply changes. Default is dry-run.")
    parser.add_argument("--collections", nargs="*", help="Collections to check (default: characters)")
    args = parser.parse_args()
    asyncio.run(main(args))
