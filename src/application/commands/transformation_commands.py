# src/application/commands/transformation_commands.py

import json
from typing import Dict, Any
from discord.ext import commands
import os

# --- Service Imports ---
from src.core.services.character_service import CharacterService
from src.core.services.transformation_service import TransformationService

# --- Repository Imports ---
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.infrastructure.database.class_repository import ClassRepository

# --- Helper Functions ---
def create_embed(title: str, description: str, color):
    return {"title": title, "description": description, "color": color}

class TransformationCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, character_service: CharacterService, transformation_service: TransformationService):
        self.bot = bot
        self.character_service = character_service
        self.transformation_service = transformation_service

    def is_master(self, ctx) -> bool:
        # Placeholder for master check
        return True

    def is_character_owner(self, ctx, character_name: str) -> bool:
        # Placeholder for owner check
        return True

    @commands.command(name="addtransformacao")
    async def add_transformation_command(self, ctx, character_name: str, transformation_name: str):
        if not self.is_master(ctx):
            await ctx.send(embed=create_embed("Erro", "Apenas Mestres podem adicionar transformações.", 0xFF0000))
            return

        if not character_name or not transformation_name:
            await ctx.send(embed=create_embed("Erro", "Uso incorreto. Exemplo: `!addtransformacao \"NomePersonagem\" \"NomeTransformacao\"`", 0xFF0000))
            return

        try:
            result = await self.transformation_service.add_transformation_to_character(character_name, transformation_name)
            await ctx.send(embed=create_embed("Sucesso", result, 0x00FF00))
        except Exception as e:
            await ctx.send(embed=create_embed("Erro", f"Ocorreu um erro ao adicionar a transformação: {e}", 0xFF0000))

    @commands.command(name="edittransformacao")
    async def edit_transformation_command(self, ctx, transformation_name: str, *, json_data_str: str):
        if not self.is_master(ctx):
            await ctx.send(embed=create_embed("Erro", "Apenas Mestres podem editar transformações.", 0xFF0000))
            return

        if not transformation_name or not json_data_str:
            await ctx.send(embed=create_embed("Erro", "Uso incorreto. Exemplo: `!edittransformacao \"NomeTransformacao\" <json_data>`", 0xFF0000))
            return

        try:
            json_data = json.loads(json_data_str)
            result = await self.transformation_service.edit_transformation(transformation_name, json_data)
            await ctx.send(embed=create_embed("Sucesso", result, 0x00FF00))
        except json.JSONDecodeError:
            await ctx.send(embed=create_embed("Erro", "Os dados JSON fornecidos são inválidos.", 0xFF0000))
        except Exception as e:
            await ctx.send(embed=create_embed("Erro", f"Ocorreu um erro ao editar a transformação: {e}", 0xFF0000))

    @commands.command(name="transformar")
    async def transform_command(self, ctx, character_name: str, transformation_name: str):
        if not self.is_character_owner(ctx, character_name):
            await ctx.send(embed=create_embed("Erro", "Você só pode ativar transformações para seus próprios personagens.", 0xFF0000))
            return

        if not character_name or not transformation_name:
            await ctx.send(embed=create_embed("Erro", "Uso incorreto. Exemplo: `!transformar \"NomePersonagem\" \"NomeTransformacao\"`", 0xFF0000))
            return

        try:
            # Assuming a default duration for activation, e.g., 300 seconds (5 minutes)
            duration_seconds = 300
            character = await self.character_service.get_character(character_name)
            transformation = await self.transformation_service.get_transformation_by_name(transformation_name)
            
            if character and transformation:
                updated_character = await self.character_service.activate_transformation(str(character.id), str(transformation.id), duration_seconds)
            else:
                raise Exception("Personagem ou transformação não encontrados.")
            await ctx.send(embed=create_embed("Sucesso", f"Transformação '{transformation_name}' ativada para '{character_name}'.", 0x00FF00))
        except Exception as e:
            await ctx.send(embed=create_embed("Erro", f"Ocorreu um erro ao ativar a transformação: {e}", 0xFF0000))

    @commands.command(name="destransformar")
    async def detransform_command(self, ctx, character_name: str, transformation_name: str):
        if not self.is_character_owner(ctx, character_name):
            await ctx.send(embed=create_embed("Erro", "Você só pode desativar transformações para seus próprios personagens.", 0xFF0000))
            return

        if not character_name or not transformation_name:
            await ctx.send(embed=create_embed("Erro", "Uso incorreto. Exemplo: `!destransformar \"NomePersonagem\" \"NomeTransformacao\"`", 0xFF0000))
            return

        try:
            character = await self.character_service.get_character(character_name)
            transformation = await self.transformation_service.get_transformation_by_name(transformation_name)
            
            if character and transformation:
                updated_character = await self.character_service.deactivate_transformation(str(character.id), str(transformation.id))
            else:
                raise Exception("Personagem ou transformação não encontrados.")
            await ctx.send(embed=create_embed("Sucesso", f"Transformação '{transformation_name}' desativada para '{character_name}'.", 0x00FF00))
        except Exception as e:
            await ctx.send(embed=create_embed("Erro", f"Ocorreu um erro ao desativar a transformação: {e}", 0xFF0000))

async def setup(bot: commands.Bot):
    mongo_connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    mongo_database_name = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")

    # Repositories
    character_repo = MongoDBRepository(mongo_connection_string, mongo_database_name)
    await character_repo.connect() # Conectar assincronamente
    transformation_repo = TransformationRepository(character_repo)
    class_repo = ClassRepository(character_repo)

    # Services
    character_service = CharacterService(character_repo, transformation_repo, class_repo)
    transformation_service = TransformationService(transformation_repo)

    await bot.add_cog(TransformationCommands(bot, character_service, transformation_service))