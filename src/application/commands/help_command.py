import discord
from discord.ext import commands
from typing import Optional, Dict, List, Tuple

# Placeholder for command descriptions. In a real application, this would be dynamically generated or stored elsewhere.
# This dictionary should ideally be populated by inspecting other command modules or a central registry.
# For now, I'll hardcode a few common commands.


class HelpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.command_categories: Dict[str, List[Tuple[str, str, str]]] = {
            "🎭 Criação e Evolução de Personagem": [],
            "📜 Importação de Ficha": [],
            "🎲 Rolagem de Dados e Preferências": [],
            "✨ Transformações (Buffs)": [],
            "⚔️ Combate por Turnos": [],
            "Outros Comandos": [] # Para comandos que não se encaixam nas categorias acima
        }
        # A população das categorias será feita no on_ready ou antes de cada chamada de help
        # para garantir que todos os cogs estejam carregados.

    def populate_command_categories(self):
        # Limpa as categorias antes de popular novamente (útil se o bot recarregar cogs)
        for category in self.command_categories:
            self.command_categories[category].clear()

        for cog_name, cog in self.bot.cogs.items():
            for command in cog.get_commands():
                if not command.hidden:
                    full_command_name = command.name
                    summary = (command.help.split('\n')[0] if command.help else "Sem descrição.")
                    examples = self._extract_examples(command.help)

                    # Lógica para categorizar comandos
                    category_found = False
                    if full_command_name == "ficha":
                        # Subcomandos de ficha
                        for sub_command in command.commands:
                            sub_summary = (sub_command.help.split('\n')[0] if sub_command.help else "Sem descrição.")
                            sub_examples = self._extract_examples(sub_command.help)
                            if sub_command.name == "criar":
                                self.command_categories["🎭 Criação e Evolução de Personagem"].append((f"!{full_command_name} {sub_command.name}", sub_summary, sub_examples))
                            elif sub_command.name == "ver":
                                self.command_categories["🎭 Criação e Evolução de Personagem"].append((f"!{full_command_name} {sub_command.name}", sub_summary, sub_examples))
                            elif sub_command.name == "atualizar":
                                self.command_categories["🎭 Criação e Evolução de Personagem"].append((f"!{full_command_name} {sub_command.name}", sub_summary, sub_examples))
                            elif sub_command.name == "excluir":
                                self.command_categories["🎭 Criação e Evolução de Personagem"].append((f"!{full_command_name} {sub_command.name}", sub_summary, sub_examples))
                        category_found = True
                    elif full_command_name == "multiclasse":
                        self.command_categories["🎭 Criação e Evolução de Personagem"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "up": # Mapeia char_levelup para !up
                        self.command_categories["🎭 Criação e Evolução de Personagem"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "pontos":
                        # Subcomandos de pontos
                        for sub_command in command.commands:
                            sub_summary = (sub_command.help.split('\n')[0] if sub_command.help else "Sem descrição.")
                            sub_examples = self._extract_examples(sub_command.help)
                            if sub_command.name == "pontos":
                                self.command_categories["🎭 Criação e Evolução de Personagem"].append((f"!{full_command_name} {sub_command.name}", sub_summary, sub_examples))
                            elif sub_command.name == "gastar":
                                self.command_categories["🎭 Criação e Evolução de Personagem"].append((f"!{full_command_name} {sub_command.name}", sub_summary, sub_examples))
                            elif sub_command.name == "refund":
                                self.command_categories["🎭 Criação e Evolução de Personagem"].append((f"!{full_command_name} {sub_command.name}", sub_summary, sub_examples))
                        category_found = True
                    elif full_command_name == "import_ficha":
                        self.command_categories["📜 Importação de Ficha"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "favorito":
                        self.command_categories["🎲 Rolagem de Dados e Preferências"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "rodar":
                        self.command_categories["🎲 Rolagem de Dados e Preferências"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "addtransformacao":
                        self.command_categories["✨ Transformações (Buffs)"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "edittransformacao":
                        self.command_categories["✨ Transformações (Buffs)"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "transformar":
                        self.command_categories["✨ Transformações (Buffs)"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "destransformar":
                        self.command_categories["✨ Transformações (Buffs)"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "startcombat":
                        self.command_categories["⚔️ Combate por Turnos"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "iniciativa":
                        self.command_categories["⚔️ Combate por Turnos"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "comecar":
                        self.command_categories["⚔️ Combate por Turnos"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "dano":
                        self.command_categories["⚔️ Combate por Turnos"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "cura":
                        self.command_categories["⚔️ Combate por Turnos"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "proximo":
                        self.command_categories["⚔️ Combate por Turnos"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "endcombat":
                        self.command_categories["⚔️ Combate por Turnos"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "help":
                        # O próprio comando help não precisa ser listado na ajuda geral
                        pass
                    elif full_command_name == "progresso":
                        self.command_categories["Outros Comandos"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif full_command_name == "stats":
                        self.command_categories["Outros Comandos"].append((f"!{full_command_name}", summary, examples))
                        category_found = True
                    elif not category_found:
                        self.command_categories["Outros Comandos"].append((f"!{full_command_name}", summary, examples))

    def _extract_examples(self, help_text: Optional[str]) -> str:
        if not help_text:
            return ""
        
        examples_lines = []
        in_examples_section = False
        for line in help_text.split('\n'):
            stripped_line = line.strip()
            if stripped_line.startswith("Ex:"):
                in_examples_section = True
                examples_lines.append(stripped_line)
            elif in_examples_section:
                examples_lines.append(stripped_line)
        return "\n".join(examples_lines).strip()

    @commands.command(name='help')
    async def help_command(self, ctx: commands.Context, *, command_name: Optional[str] = None):
        """Exibe a mensagem de ajuda para todos os comandos ou para um comando específico."""
        # Recarrega as categorias para garantir que novos cogs/comandos sejam incluídos
        self.populate_command_categories()

        if command_name:
            command = self.bot.get_command(command_name)
            if command:
                # Extrair descrição e exemplos do help_text
                help_text = command.help or "Sem descrição disponível."
                description_lines = []
                examples_lines = []
                in_examples_section = False

                for line in help_text.split('\n'):
                    stripped_line = line.strip()
                    if stripped_line.startswith("Ex:"):
                        in_examples_section = True
                        examples_lines.append(stripped_line)
                    elif in_examples_section:
                        examples_lines.append(stripped_line)
                    else:
                        description_lines.append(stripped_line)
                
                description = "\n".join(description_lines).strip()
                examples = "\n".join(examples_lines).strip()

                embed = discord.Embed(
                    title=f"Ajuda: !{command.name}",
                    description=description if description else "Sem descrição disponível.",
                    color=discord.Color.blue()
                )
                if command.aliases:
                    embed.add_field(name="Apelidos", value=", ".join(command.aliases), inline=False)
                if isinstance(command, commands.Group):
                    subcommands = ", ".join([f"`!{c.name}`" for c in command.commands])
                    embed.add_field(name="Subcomandos", value=subcommands, inline=False)
                if examples:
                    embed.add_field(name="Exemplos de Uso", value=examples, inline=False)
            else:
                embed = discord.Embed(
                    title="Comando não encontrado",
                    description=f"O comando `!{command_name}` não foi encontrado. Use `!help` para ver todos os comandos.",
                    color=discord.Color.red()
                )
        else:
            embed = discord.Embed(
                title="Guia de Comandos do RPG Bot",
                description=(
                    "Bem-vindo ao guia de comandos do RPG Bot! Aqui você encontrará uma lista de todos os comandos disponíveis.\n"
                    "Use `!help <comando>` para obter detalhes específicos sobre um comando, incluindo exemplos de uso.\n\n"
                    "**Categorias de Comandos:**"
                ),
                color=discord.Color.green()
            )
            
            for category_name, commands_in_category in self.command_categories.items():
                if commands_in_category:
                    commands_list_str = []
                    for cmd_name, summary, examples in commands_in_category:
                        commands_list_str.append(f"`{cmd_name}` - {summary}")
                        if examples:
                            # Adiciona exemplos formatados para a ajuda geral, se houver
                            commands_list_str.append(f"```\n{examples}\n```")
                    
                    embed.add_field(
                        name=category_name,
                        value="\n".join(commands_list_str),
                        inline=False
                    )
            embed.set_footer(text="Para ajuda mais detalhada ou suporte, entre em contato com o administrador do bot.")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    # Remove default discord.py help command if present to avoid registration conflicts
    try:
        bot.remove_command('help')
    except Exception:
        pass
    await bot.add_cog(HelpCommand(bot))