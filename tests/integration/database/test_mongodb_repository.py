import unittest
from unittest.mock import patch, MagicMock
from pymongo.errors import ConnectionFailure, PyMongoError
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.core.entities.character import Character
from src.utils.exceptions.infrastructure_exceptions import DatabaseConnectionError, RepositoryError
import mongomock
import re
from typing import cast

class TestMongoDBRepository(unittest.TestCase):

    @patch('pymongo.MongoClient', new_callable=mongomock.MongoClient)
    def setUp(self, MockMongoClient):
        self.connection_string = "mongodb://localhost:27017/"
        self.database_name = "test_rpg_db"
        self.collection_name = "test_characters"
        self.repo = MongoDBRepository(self.connection_string, self.database_name, self.collection_name)
        self.addCleanup(self.repo.disconnect) # Ensure disconnect is called after each test
        self.assertIsNotNone(self.repo.collection)
        cast(MagicMock, self.repo.collection).delete_many({}) # Clear collection before each test

    # O tearDown não é mais necessário, pois addCleanup() garante o disconnect
    # def tearDown(self):
    #     self.repo.disconnect()

    def test_connection_success(self):
        self.assertIsNotNone(self.repo.client)
        self.assertIsNotNone(self.repo.db)
        self.assertIsNotNone(self.repo.collection)

    @patch('src.infrastructure.database.mongodb_repository.MongoClient')
    def test_connection_failure(self, MockMongoClient):
        MockMongoClient.side_effect = ConnectionFailure("Test connection failure")
        with self.assertRaises(DatabaseConnectionError):
            MongoDBRepository(self.connection_string, self.database_name, self.collection_name) # A conexão falhará na inicialização

    def test_save_character(self):
        character = Character(name="Gandalf", class_name="Wizard")
        inserted_id = self.repo.save_character(character)
        self.assertIsNotNone(inserted_id)
        retrieved_character = self.repo.get_character(character.id)
        self.assertIsNotNone(retrieved_character) # Ensure character is not None
        retrieved_character = cast(Character, retrieved_character)
        self.assertEqual(retrieved_character.name, "Gandalf")

    def test_get_character(self):
        character = Character(name="Aragorn", class_name="Ranger")
        self.repo.save_character(character)
        retrieved_character = self.repo.get_character(character.id)
        self.assertIsNotNone(retrieved_character) # Ensure character is not None
        retrieved_character = cast(Character, retrieved_character)
        self.assertEqual(retrieved_character.name, "Aragorn")
        self.assertIsInstance(retrieved_character, Character)

    def test_get_character_not_found(self):
        retrieved_character = self.repo.get_character("non_existent_id")
        self.assertIsNone(retrieved_character)

    def test_get_character_by_name_or_alias(self):
        char1 = Character(name="Frodo", class_name="Hobbit", alias="Ring-bearer")
        char2 = Character(name="Samwise", class_name="Hobbit")
        self.repo.save_character(char1)
        self.repo.save_character(char2)

        found_char_by_name = self.repo.get_character_by_name_or_alias("Frodo")
        self.assertIsNotNone(found_char_by_name) # Ensure character is not None
        found_char_by_name = cast(Character, found_char_by_name)
        self.assertEqual(found_char_by_name.name, "Frodo")

        found_char_by_alias = self.repo.get_character_by_name_or_alias("Ring-bearer")
        self.assertIsNotNone(found_char_by_alias) # Ensure character is not None
        found_char_by_alias = cast(Character, found_char_by_alias)
        self.assertEqual(found_char_by_alias.name, "Frodo")

        found_char_case_insensitive = self.repo.get_character_by_name_or_alias("frodo")
        self.assertIsNotNone(found_char_case_insensitive) # Ensure character is not None
        found_char_case_insensitive = cast(Character, found_char_case_insensitive)
        self.assertEqual(found_char_case_insensitive.name, "Frodo")

        not_found_char = self.repo.get_character_by_name_or_alias("Gimli")
        self.assertIsNone(not_found_char)

    def test_update_character(self):
        character = Character(name="Legolas", class_name="Elf")
        self.repo.save_character(character)
        
        character.level = 2
        character.alias = "Greenleaf"
        updated = self.repo.update_character(character)
        self.assertTrue(updated)

        retrieved_character = self.repo.get_character(character.id)
        self.assertIsNotNone(retrieved_character) # Ensure character is not None
        retrieved_character = cast(Character, retrieved_character)
        self.assertEqual(retrieved_character.level, 2)
        self.assertEqual(retrieved_character.alias, "Greenleaf")

    def test_update_character_not_found(self):
        character = Character(name="Boromir", class_name="Human")
        # Don't save the character
        updated = self.repo.update_character(character)
        self.assertFalse(updated)

    def test_delete_character(self):
        character = Character(name="Gollum", class_name="Creature")
        self.repo.save_character(character)
        
        deleted = self.repo.delete_character(character.id)
        self.assertTrue(deleted)

        retrieved_character = self.repo.get_character(character.id)
        self.assertIsNone(retrieved_character)

    def test_delete_character_not_found(self):
        deleted = self.repo.delete_character("non_existent_id")
        self.assertFalse(deleted)

    def test_get_all_characters(self):
        char1 = Character(name="Pippin", class_name="Hobbit")
        char2 = Character(name="Merry", class_name="Hobbit")
        self.repo.save_character(char1)
        self.repo.save_character(char2)

        all_characters = self.repo.get_all_characters()
        self.assertEqual(len(all_characters), 2)
        self.assertTrue(any(c.name == "Pippin" for c in all_characters))
        self.assertTrue(any(c.name == "Merry" for c in all_characters))

    def test_repository_error_on_save(self):
        # Simulate a PyMongoError during insert_one
        with patch.object(self.repo.collection, 'insert_one', side_effect=PyMongoError("Test PyMongoError")):
            character = Character(name="ErrorChar", class_name="ErrorClass")
            with self.assertRaises(RepositoryError):
                self.repo.save_character(character)

    def test_repository_error_on_get(self):
        # Simulate a PyMongoError during find_one
        with patch.object(self.repo.collection, 'find_one', side_effect=PyMongoError("Test PyMongoError")):
            with self.assertRaises(RepositoryError):
                self.repo.get_character("some_id")

if __name__ == '__main__':
    unittest.main()