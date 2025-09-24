import asyncio
from unittest import TestCase
from unittest.mock import AsyncMock, Mock
from bson.objectid import ObjectId

from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.core.entities.character import Character


class TestMongoDBRepositoryIDHandling(TestCase):
    def test_update_character_with_string_id_converted_to_objectid(self):
        # Arrange
        repo = MongoDBRepository("mongodb://localhost:27017", "testdb")
        # Mock collection
        mock_collection = Mock()
        mock_collection.replace_one = AsyncMock(return_value=Mock(acknowledged=True, modified_count=1))
        repo.characters_collection = mock_collection
        # Create a character with id as string (simulating the problematic case)
        char_id_str = "68cc6201929d8d292f1a1c7f"
        character = Character(name="TestChar")
        # Bypass static type checks and set a string id to simulate stored string IDs
        object.__setattr__(character, "id", char_id_str)

        # Act
        result = asyncio.run(repo.update_character(character))

        # Assert
        self.assertTrue(result)
        # Ensure replace_one was called with an ObjectId in the filter
        called_args, called_kwargs = mock_collection.replace_one.call_args
        filter_arg = called_args[0]
        self.assertIn("_id", filter_arg)
        self.assertIsInstance(filter_arg["_id"], ObjectId)
