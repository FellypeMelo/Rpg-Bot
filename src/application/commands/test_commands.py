import discord
from discord.ext import commands
from typing import List, Dict, Any, Optional
import os
import asyncio

from src.core.services.character_service import CharacterService
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.player_preferences_repository import PlayerPreferencesRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.infrastructure.database.class_repository import ClassRepository
from src.core.entities.player_preferences import PlayerPreferences
from src.utils.exceptions.application_exceptions import CharacterNotFoundError, InvalidInputError

class TestCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, character_service: CharacterService, player_preferences_repository: PlayerPreferencesRepository):
        self.bot = bot
        self.character_service = character_service
        self.player_preferences_repository = player_preferences_repository
        self.test_character_id: Optional[str] = None
        self.test_character_name: Optional[str] = None

    @commands.command(name="criar_personagem_teste", help="Cria um personagem para ser usado nos testes e o define como favorito.")
    async def create_test_character(self, ctx: commands.Context, name: str, class_name: str):
        try:
            character = await self.character_service.create_character(
                name=name,
                player_discord_id=str(ctx.author.id),
                class_name=class_name,
            )
            self.test_character_id = str(character.id)
            self.test_character_name = character.name

            preferences = await self.player_preferences_repository.get_preferences(str(ctx.author.id))
            if not preferences:
                preferences = PlayerPreferences(player_discord_id=str(ctx.author.id))
            preferences.favorite_character_id = self.test_character_id
            await self.player_preferences_repository.save_preferences(preferences)

            embed = discord.Embed(
                title=f"Personagem de Teste '{character.name}' criado e definido como favorito!",
                description=f"ID: `{character.id}`\nClasse: {character.class_name}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Erro ao criar personagem de teste: {e}")

    @commands.command(name="limpar_personagem_teste", help="Exclui o personagem de teste criado.")
    async def clear_test_character(self, ctx: commands.Context):
        if not self.test_character_id:
            await ctx.send("Nenhum personagem de teste ativo para limpar.")
            return

        try:
            # Remover das preferências do jogador se for o favorito
            preferences = await self.player_preferences_repository.get_preferences(str(ctx.author.id))
            if preferences and preferences.favorite_character_id == self.test_character_id:
                preferences.favorite_character_id = None
                await self.player_preferences_repository.save_preferences(preferences)

            await self.character_service.delete_character(self.test_character_id)
            embed = discord.Embed(
                title=f"Personagem de Teste '{self.test_character_name}' excluído!",
                description=f"ID: `{self.test_character_id}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            self.test_character_id = None
            self.test_character_name = None
        except Exception as e:
            await ctx.send(f"Erro ao limpar personagem de teste: {e}")

    @commands.command(name="testar_comandos", help="Testa todos os comandos registrados no bot.")
    async def test_all_commands(self, ctx: commands.Context):
        """
        Testa todos os comandos do bot, simulando chamadas e reportando o status.
        """
        if not self.test_character_id:
            await ctx.send("Por favor, crie um personagem de teste primeiro usando `!criar_personagem_teste <nome> <classe>`.")
            return

        results = []
        await ctx.send("Iniciando testes de comandos... Isso pode levar um tempo.")

        for cog_name, cog in self.bot.cogs.items():
            for command in cog.get_commands():
                if command.hidden or command.name in ["criar_personagem_teste", "limpar_personagem_teste", "testar_comandos"]:
                    continue

                test_result = await self._test_single_command(ctx, command)
                results.append(test_result)
        
        # Gerar relatório final
        success_count = sum(1 for r in results if r["status"] == "SUCESSO")
        fail_count = len(results) - success_count

        report_embed = discord.Embed(
            title="Relatório de Testes de Comandos",
            description=f"Total de Comandos Testados: {len(results)}\n"
                        f"✅ Sucessos: {success_count}\n"
                        f"❌ Falhas: {fail_count}",
            color=discord.Color.blue()
        )

        for result in results:
            status_emoji = "✅" if result["status"] == "SUCESSO" else "❌"
            report_embed.add_field(
                name=f"{status_emoji} !{result['command_name']}",
                value=f"Status: {result['status']}\nDetalhes: {result['details']}",
                inline=False
            )
        
        await ctx.send(embed=report_embed)

    async def _test_single_command(self, ctx: commands.Context, command: commands.Command) -> Dict[str, Any]:
        command_name = command.name
        details = "N/A"
        status = "FALHA" # Assume falha por padrão

        try:
            # Para comandos sem argumentos obrigatórios, apenas invocar
            if not command.clean_params:
                await command(ctx)
                status = "SUCESSO"
                details = "Comando invocado sem argumentos."
            else:
                # Lógica para comandos com argumentos
                if command_name == "ficha":
                    if command.name == "criar":
                        await command(ctx, "PersonagemTeste", "Guerreiro")
                        status = "SUCESSO"
                        details = "Comando 'ficha criar' testado com sucesso."
                    elif command.name == "ver":
                        if self.test_character_id:
                            await command(ctx, self.test_character_id)
                            status = "SUCESSO"
                            details = f"Comando 'ficha ver' testado com personagem de teste: {self.test_character_name}."
                        else:
                            details = "Personagem de teste não criado."
                    elif command.name == "atualizar":
                        if self.test_character_id:
                            await command(ctx, self.test_character_id, "name", value="PersonagemAtualizado")
                            status = "SUCESSO"
                            details = f"Comando 'ficha atualizar' testado com personagem de teste: {self.test_character_name}."
                        else:
                            details = "Personagem de teste não criado."
                    elif command.name == "excluir":
                        # Excluir é um comando destrutivo, não testar automaticamente
                        details = "Comando 'ficha excluir' é destrutivo, teste manual necessário."
                    else:
                        details = f"Subcomando de 'ficha' '{command.name}' não suportado no teste automático."
                elif command_name == "progresso":
                    if self.test_character_id:
                        await command(ctx, self.test_character_id)
                        status = "SUCESSO"
                        details = f"Comando 'progresso' testado com personagem de teste: {self.test_character_name}."
                    else:
                        details = "Personagem de teste não criado."
                elif command_name == "up":
                    if self.test_character_id:
                        await command(ctx, self.test_character_id, 1) # Sobe 1 nível
                        status = "SUCESSO"
                        details = f"Comando 'up' testado com personagem de teste: {self.test_character_name}."
                    else:
                        details = "Personagem de teste não criado."
                elif command_name == "dano":
                    if self.test_character_id:
                        await command(ctx, 5, self.test_character_name) # Causa 5 de dano
                        status = "SUCESSO"
                        details = f"Comando 'dano' testado com personagem de teste: {self.test_character_name}."
                    else:
                        details = "Personagem de teste não criado."
                elif command_name == "cura":
                    if self.test_character_id:
                        await command(ctx, 5, self.test_character_name) # Cura 5
                        status = "SUCESSO"
                        details = f"Comando 'cura' testado com personagem de teste: {self.test_character_name}."
                    else:
                        details = "Personagem de teste não criado."
                elif command_name == "favorito":
                    if self.test_character_id:
                        await command(ctx, self.test_character_id)
                        status = "SUCESSO"
                        details = f"Comando 'favorito' testado com personagem de teste: {self.test_character_name}."
                    else:
                        details = "Personagem de teste não criado."
                elif command_name == "import_ficha":
                    details = "Comando 'import_ficha' requer sheet_text formatado, teste manual necessário."
                elif command_name == "multiclasse":
                    if self.test_character_id:
                        # Assumindo que 'Mago' é uma classe válida para multiclasse
                        await command(ctx, self.test_character_name, "Mago")
                        status = "SUCESSO"
                        details = f"Comando 'multiclasse' testado com personagem de teste: {self.test_character_name}."
                    else:
                        details = "Personagem de teste não criado."
                elif command_name == "addtransformacao":
                    details = "Comando 'addtransformacao' requer permissão de mestre e dados de transformação, teste manual necessário."
                elif command_name == "edittransformacao":
                    details = "Comando 'edittransformacao' requer permissão de mestre e dados de transformação, teste manual necessário."
                elif command_name == "transformar":
                    details = "Comando 'transformar' requer transformação existente, teste manual necessário."
                elif command_name == "destransformar":
                    details = "Comando 'destransformar' requer transformação ativa, teste manual necessário."
                elif command_name == "pontos":
                    # Testar subcomandos de pontos
                    if command.name == "pontos": # !pontos pontos
                        if self.test_character_name:
                            await command(ctx, self.test_character_name)
                            status = "SUCESSO"
                            details = f"Comando 'pontos pontos' testado com personagem de teste: {self.test_character_name}."
                        else:
                            details = "Personagem de teste não criado."
                    elif command.name == "gastar":
                        if self.test_character_name:
                            # Assumindo que o personagem de teste tem pontos para gastar
                            await command(ctx, "status", self.test_character_name, 1)
                            status = "SUCESSO"
                            details = f"Comando 'pontos gastar status' testado com personagem de teste: {self.test_character_name}."
                        else:
                            details = "Personagem de teste não criado."
                    elif command.name == "refund":
                        if self.test_character_name:
                            # Assumindo que o personagem de teste tem pontos gastos para reembolsar
                            details = "Comando 'pontos refund' requer pontos gastos específicos, teste manual necessário."
                        else:
                            details = "Personagem de teste não criado."
                    else:
                        details = f"Subcomando de 'pontos' '{command.name}' não suportado no teste automático."
                elif command_name == "help":
                    await command(ctx)
                    status = "SUCESSO"
                    details = "Comando 'help' invocado sem argumentos."
                elif command_name == "stats":
                    await command(ctx)
                    status = "SUCESSO"
                    details = "Comando 'stats' invocado sem argumentos."
                elif command_name == "rodar":
                    if self.test_character_id:
                        await command(ctx, "força", 5) # Rola força com bônus de 5
                        status = "SUCESSO"
                        details = f"Comando 'rodar' testado com personagem de teste: {self.test_character_name}."
                    else:
                        details = "Personagem de teste não criado."
                else:
                    details = "Comando com argumentos obrigatórios, teste automático não implementado."
                    
        except commands.MissingRequiredArgument as e:
            details = f"FALHA: Argumento obrigatório faltando: {e}"
        except commands.BadArgument as e:
            details = f"FALHA: Argumento inválido: {e}"
        except Exception as e:
            details = f"FALHA: Erro inesperado: {e}"
        
        return {"command_name": command_name, "status": status, "details": details}

async def setup(bot: commands.Bot):
    connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    database_name = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")

    mongodb_repo = MongoDBRepository(
        connection_string=connection_string,
        database_name=database_name
    )
    await mongodb_repo.connect()

    character_repo = mongodb_repo
    transformation_repo = TransformationRepository(mongodb_repo)
    class_repo = ClassRepository(mongodb_repo)
    player_preferences_repo = PlayerPreferencesRepository(mongodb_repository=mongodb_repo)

    character_service = CharacterService(
        character_repository=character_repo,
        transformation_repository=transformation_repo,
        class_repository=class_repo
    )
    await bot.add_cog(TestCommands(bot, character_service, player_preferences_repo))