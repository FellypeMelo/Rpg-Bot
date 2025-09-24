import discord
from discord.ext import commands
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
import sys
from pathlib import Path
# Adiciona diretório raiz do projeto ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Load environment variables from .env file
load_dotenv()

class RPGDiscordBot(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.initial_extensions = [
            'src.application.commands.character_commands',
            'src.application.commands.points_commands',
            'src.application.commands.levelup_commands',
            'src.application.commands.combat_commands',
            'src.application.commands.report_commands',
            'src.application.commands.dice_commands',
            'src.application.commands.help_command',
            'src.application.commands.test_commands',
        ]

    async def setup_hook(self):
        for extension in self.initial_extensions:
            await self.load_extension(extension)
        print(f"Extensions loaded: {', '.join(self.initial_extensions)}")

    async def on_ready(self):
        if self.user:
            print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_command_error(self, context: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            await context.send("Comando não encontrado. Use `!ajuda` para ver os comandos disponíveis.")
        elif isinstance(error, commands.MissingRequiredArgument):
            if context.command:
                await context.send(f"Argumentos faltando: {error}. Verifique `!ajuda {context.command.name}`.")
            else:
                await context.send(f"Argumentos faltando: {error}.")
        elif isinstance(error, commands.BadArgument):
            if context.command:
                await context.send(f"Argumento inválido: {error}. Verifique `!ajuda {context.command.name}`.")
            else:
                await context.send(f"Argumento inválido: {error}.")
        elif isinstance(error, commands.MissingPermissions):
            await context.send("Você não tem permissão para usar este comando.")
        elif isinstance(error, commands.NotOwner):
            await context.send("Este comando só pode ser usado pelo proprietário do bot.")
        else:
            print(f"Ignoring exception in command {context.command}:", error)
            await context.send(f"Ocorreu um erro inesperado: {error}")

def run_bot():
    intents = discord.Intents.default()
    intents.message_content = True # Required for accessing message.content
    intents.members = True # Required for member-related events/commands

    bot = RPGDiscordBot(command_prefix='!', intents=intents)

    # Get Discord token from environment variables
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    if DISCORD_TOKEN is None:
        raise ValueError("DISCORD_TOKEN não encontrado nas variáveis de ambiente.")

    bot.run(DISCORD_TOKEN)

if __name__ == '__main__':
    run_bot()