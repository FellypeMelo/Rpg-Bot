import discord
from discord.ext import commands
import logging
from typing import Optional, List, Dict, Any, Tuple
import re # For parsing initiative arguments

from src.core.services.combat_service import CombatService
from src.core.entities.combat_session import CombatSession # Assuming this is needed for type hinting
from src.core.entities.character import Character # Assuming this is needed for type hinting
from src.application.dtos.combat_dto import (
    InitiativeEntryDTO, StartCombatSessionDTO, ApplyDamageHealingDTO,
    EndCombatSessionDTO, CombatSessionResponseDTO
)
from src.utils.exceptions.application_exceptions import (
    CombatError, CombatSessionNotFoundError, CharacterNotFoundError,
    MaxCombatSessionsError, InvalidInputError, InvalidCharacterError,
    CharacterError, AppPermissionError
)
from src.utils.exceptions.infrastructure_exceptions import RepositoryError
from src.infrastructure.database.mongodb_repository import MongoDBRepository # For instantiation
from src.infrastructure.database.player_preferences_repository import PlayerPreferencesRepository
from src.infrastructure.cache.redis_repository import RedisRepository # For instantiation
import os

# Helper function to create embeds
def create_embed(title: str, description: str, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)

class CombatCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, combat_service: CombatService):
        self.bot = bot
        self.combat_service = combat_service
        self.logger = logging.getLogger(__name__)

    async def get_session_id_from_context(self, context: commands.Context) -> str:
        """Retrieves the active combat session ID for the current channel/guild."""
        command_name = context.command.name if context.command else "UnknownCommand"
        self.logger.debug(f"[{command_name}] - Iniciando get_session_id_from_context para guild_id: {context.guild.id if context.guild else 'DM'}, channel_id: {context.channel.id}")
        guild_id = str(context.guild.id) if context.guild else "DM"
        channel_id = str(context.channel.id)
        try:
            self.logger.debug(f"[{command_name}] - Chamando combat_service.get_active_session_id para guild_id: {guild_id}, channel_id: {channel_id}")
            session_id = await self.combat_service.get_active_session_id(guild_id, channel_id)
            self.logger.debug(f"[{command_name}] - Retorno de combat_service.get_active_session_id: {session_id}")
            if not session_id:
                self.logger.warning(f"[{command_name}] - Nenhuma sessão de combate ativa encontrada para guild_id: {guild_id}, channel_id: {channel_id}")
                raise CombatSessionNotFoundError("Nenhuma sessão de combate ativa neste canal.")
            self.logger.info(f"[{command_name}] - Sessão de combate ativa recuperada: {session_id}")
            return session_id
        except CombatSessionNotFoundError as e:
            self.logger.error(f"[{command_name}] - CombatSessionNotFoundError em get_session_id_from_context: {e}")
            await context.send(embed=create_embed("Erro de Combate", str(e), discord.Color.red()))
            raise # Re-raise to prevent further execution
        except Exception as e:
            self.logger.critical(f"[{command_name}] - Erro inesperado em get_session_id_from_context: {e}", exc_info=True)
            await context.send(embed=create_embed("Erro Inesperado", f"Ocorreu um erro inesperado ao obter a sessão: {e}", discord.Color.red()))
            raise

    async def get_character_data(self, identifier: str, context: commands.Context) -> Optional[Character]:
        """Fetches character data, handling both ID and name, and validates ownership if applicable."""
        player_id = str(context.author.id)

        try:
            # Prioriza a busca por nome, que é o caso de uso mais comum em comandos.
            character = await self.combat_service.get_character_by_name(identifier)
            if character:
                # A verificação de dono não deve ser tão restritiva aqui,
                # pois um mestre pode precisar referenciar personagens de jogadores.
                # A lógica de permissão específica deve ficar nos comandos.
                return character
        except CharacterNotFoundError:
            # Se não encontrar por nome, tenta por ID.
            try:
                character = await self.combat_service.get_character_by_id(identifier)
                if character:
                    return character
            except (RepositoryError, CharacterNotFoundError): # RepositoryError pode ocorrer se o ID for inválido
                # Se falhar a busca por ID também, então o personagem não foi encontrado.
                raise CharacterNotFoundError(f"Personagem '{identifier}' não encontrado.")
        except Exception as e:
            self.logger.error(f"Erro inesperado ao buscar dados do personagem '{identifier}': {e}", exc_info=True)
            await context.send(embed=create_embed("Erro Inesperado", f"Erro ao buscar personagem '{identifier}': {e}", discord.Color.red()))
            raise
        
        # Se chegou até aqui, o personagem não foi encontrado.
        raise CharacterNotFoundError(f"Personagem '{identifier}' não encontrado.")
    async def get_player_character_session(self, context: commands.Context) -> tuple[str, str]:
        """Gets the player's current combat session ID and character ID."""
        command_name = context.command.name if context.command else "UnknownCommand"
        self.logger.debug(f"[{command_name}] - Iniciando get_player_character_session para player_id: {context.author.id}, guild_id: {context.guild.id if context.guild else 'DM'}, channel_id: {context.channel.id}")
        player_id = str(context.author.id)
        guild_id = str(context.guild.id) if context.guild else "DM"
        channel_id = str(context.channel.id)
        try:
            self.logger.debug(f"[{command_name}] - Chamando combat_service.get_player_character_session para player_id: {player_id}, guild_id: {guild_id}, channel_id: {channel_id}")
            session_id, character_id = await self.combat_service.get_player_character_session(player_id, guild_id, channel_id)
            self.logger.debug(f"[{command_name}] - Retorno de combat_service.get_player_character_session: session_id={session_id}, character_id={character_id}")
            self.logger.info(f"[{command_name}] - Sessão e personagem do jogador recuperados: session_id={session_id}, character_id={character_id}")
            return session_id, character_id
        except CombatSessionNotFoundError as e:
            self.logger.error(f"[{command_name}] - CombatSessionNotFoundError em get_player_character_session: {e}")
            await context.send(embed=create_embed("Erro de Combate", str(e), discord.Color.red()))
            raise
        except Exception as e:
            self.logger.critical(f"[{command_name}] - Erro inesperado em get_player_character_session: {e}", exc_info=True)
            await context.send(embed=create_embed("Erro Inesperado", f"Ocorreu um erro inesperado ao obter a sessão: {e}", discord.Color.red()))
            raise

    # --- Command Implementations ---

    @commands.command(name="startcombat")
    async def start_combat(self, context: commands.Context):
        """
        (Mestre) Inicia uma sessão de combate no canal atual.
        """
        command_name = context.command.name if context.command else "UnknownCommand"
        self.logger.debug(f"[{command_name}] - Iniciando start_combat para guild_id: {context.guild.id if context.guild else 'DM'}, channel_id: {context.channel.id}, player_id: {context.author.id}")
        # Mestre check would ideally go here, but assuming CombatService handles permissions or context implies Mestre
        guild_id = str(context.guild.id) if context.guild else "DM"
        channel_id = str(context.channel.id)
        player_id = str(context.author.id) # The player initiating the combat (assumed Mestre)

        try:
            self.logger.debug(f"[{command_name}] - Chamando combat_service.start_combat_session com guild_id: {guild_id}, channel_id: {channel_id}, player_id: {player_id}")
            session = await self.combat_service.start_combat_session(
                guild_id=guild_id,
                channel_id=channel_id,
                player_id=player_id # Player who initiated the combat
            )
            self.logger.info(f"[{command_name}] - Sessão de combate criada com sucesso. ID: {session.id}")
            
            embed = create_embed(
                "Sessão de Combate Iniciada",
                f"Uma nova sessão de combate foi iniciada no canal. Use `!iniciativa` para adicionar participantes.",
                discord.Color.green()
            )
            embed.add_field(name="ID da Sessão", value=f"`{session.id}`", inline=False)
            embed.add_field(name="Iniciado por", value=f"<@{player_id}>", inline=False)
            await context.send(embed=embed)

        except MaxCombatSessionsError as e:
            self.logger.error(f"[{command_name}] - MaxCombatSessionsError em start_combat: {e}")
            await context.send(embed=create_embed("Erro de Combate", str(e), discord.Color.red()))
        except CombatError as e:
            self.logger.error(f"[{command_name}] - CombatError em start_combat: {e}")
            await context.send(embed=create_embed("Erro de Combate", f"Erro ao iniciar combate: {e}", discord.Color.red()))
        except Exception as e:
            self.logger.critical(f"[{command_name}] - Erro inesperado em start_combat: {e}", exc_info=True)
            await context.send(embed=create_embed("Erro Inesperado", f"Ocorreu um erro inesperado ao iniciar o combate: {e}", discord.Color.red()))

    @commands.command(name="iniciativa")
    async def add_initiative(self, context: commands.Context, *, participants_str: str):
        """
        Adiciona personagens (jogadores e NPCs) à ordem de iniciativa.
        Ex: !iniciativa "Guerreiro", "Orc+2", "Mago"
        """
        command_name = context.command.name if context.command else "UnknownCommand"
        self.logger.debug(f"[{command_name}] - Iniciando add_initiative para guild_id: {context.guild.id if context.guild else 'DM'}, channel_id: {context.channel.id}, player_id: {context.author.id}, participants_str: {participants_str}")
        session_id = await self.get_session_id_from_context(context)
        guild_id = str(context.guild.id) if context.guild else "DM"
        player_id = str(context.author.id)

        # Split participants by comma, then strip quotes and spaces.
        participants = [p.strip().strip('"') for p in participants_str.split(',')]
        self.logger.debug(f"[{command_name}] - Participantes parseados: {participants}")
        
        initiative_entries_to_add: List[InitiativeEntryDTO] = []
        
        for participant_name_raw in participants:
            name = participant_name_raw.strip()
            modifier = 0
            character_id = None # For player characters
            is_npc = False
            self.logger.debug(f"[{command_name}] - Processando participante: {participant_name_raw}")

            if '+' in name:
                parts = name.rsplit('+', 1) # Split only on the last '+'
                name = parts[0].strip()
                try:
                    modifier = int(parts[1].strip())
                    self.logger.debug(f"[{command_name}] - Modificador extraído: {modifier} para {name}")
                except ValueError:
                    self.logger.warning(f"[{command_name}] - Modificador inválido para '{participant_name_raw}'.")
                    await context.send(embed=create_embed("Entrada Inválida", f"Modificador inválido para '{participant_name_raw}'. Use o formato 'Nome+Modificador'.", discord.Color.red()))
                    return
            
            try:
                self.logger.debug(f"[{command_name}] - Tentando obter dados do personagem para '{name}'")
                character = await self.get_character_data(name, context)
                if character:
                    character_id = character.id
                    self.logger.debug(f"[{command_name}] - Personagem encontrado: {character.name} ({character.id})")
                # Use dexterity modifier from character.
                dex_modifier = character.modifiers.get("dexterity", 0) if character and character.modifiers else 0
                initiative_modifier = dex_modifier + modifier # Add explicit modifier from command
                self.logger.debug(f"[{command_name}] - Modificador de iniciativa calculado para {name}: {initiative_modifier} (Dex: {dex_modifier}, Extra: {modifier})")
                
                initiative_entries_to_add.append(InitiativeEntryDTO(
                    session_id=session_id,
                    character_id=str(character_id) if character_id else None,
                    character_name=name,
                    player_id=player_id,
                    modifier=initiative_modifier,
                    is_npc=False
                ))
                self.logger.debug(f"[{command_name}] - Adicionado PC '{name}' à lista de iniciativa.")
                
            except (CharacterNotFoundError, InvalidCharacterError):
                self.logger.debug(f"[{command_name}] - Personagem '{name}' não encontrado como PC, tratando como NPC.")
                # If not found as a player character, treat as NPC
                is_npc = True
                initiative_entries_to_add.append(InitiativeEntryDTO(
                    session_id=session_id,
                    character_name=name,
                    player_id=player_id,
                    modifier=modifier,
                    is_npc=True
                ))
                self.logger.debug(f"[{command_name}] - Adicionado NPC '{name}' à lista de iniciativa.")
            except Exception as e:
                self.logger.critical(f"[{command_name}] - Erro inesperado ao processar participante '{participant_name_raw}': {e}", exc_info=True)
                await context.send(embed=create_embed("Erro Inesperado", f"Erro ao processar participante '{participant_name_raw}': {e}", discord.Color.red()))
                continue

        if not initiative_entries_to_add:
            self.logger.warning(f"[{command_name}] - Nenhum participante válido foi fornecido para adicionar à iniciativa.")
            await context.send(embed=create_embed("Nenhum Participante", "Nenhum participante válido foi fornecido para adicionar à iniciativa.", discord.Color.orange()))
            return

        try:
            self.logger.debug(f"[{command_name}] - Chamando combat_service.add_characters_to_initiative com session_id: {session_id}, entries: {len(initiative_entries_to_add)}")
            await self.combat_service.add_characters_to_initiative(session_id, initiative_entries_to_add)
            self.logger.info(f"[{command_name}] - Personagens adicionados à iniciativa com sucesso.")
            
            self.logger.debug(f"[{command_name}] - Chamando combat_service.get_initiative_order para session_id: {session_id}")
            initiative_order = await self.combat_service.get_initiative_order(session_id)
            self.logger.debug(f"[{command_name}] - Ordem de iniciativa recuperada: {initiative_order}")
            
            if not initiative_order:
                self.logger.warning(f"[{command_name}] - Ordem de iniciativa vazia após adicionar participantes.")
                await context.send(embed=create_embed("Iniciativa Vazia", "Nenhum participante foi adicionado à iniciativa ainda.", discord.Color.orange()))
                return

            description = "Ordem de Iniciativa:\n"
            for i, entry in enumerate(initiative_order):
                char_name = entry.get("name", "N/A")
                initiative_value = entry.get("initiative", 0)
                player_info = f" (<@{entry.get('player_id')}>)" if entry.get("player_id") and entry.get("type") == "player" else ""
                description += f"**{initiative_value}** - **{char_name}**{player_info}\n"
            self.logger.info(f"[{command_name}] - Ordem de iniciativa formatada para exibição.")

            embed = create_embed(
                "Iniciativa Atualizada",
                description,
                discord.Color.green()
            )
            await context.send(embed=embed)

        except (CombatSessionNotFoundError, InvalidInputError, CombatError) as e:
            self.logger.error(f"[{command_name}] - Erro de combate ao adicionar à iniciativa: {e}")
            await context.send(embed=create_embed("Erro de Combate", f"Erro ao adicionar à iniciativa: {e}", discord.Color.red()))
        except Exception as e:
            self.logger.critical(f"[{command_name}] - Erro inesperado ao gerenciar a iniciativa: {e}", exc_info=True)
            await context.send(embed=create_embed("Erro Inesperado", f"Ocorreu um erro inesperado ao gerenciar a iniciativa: {e}", discord.Color.red()))

    @commands.command(name="comecar")
    async def start_combat_turn(self, context: commands.Context):
        """
        (Mestre) Inicia os turnos do combate.
        """
        try:
            session_id = await self.get_session_id_from_context(context)
            
            # Assuming CombatService.start_combat_turn returns info about the first turn
            turn_info = await self.combat_service.start_combat_turn(session_id)
            
            current_character_name = turn_info.get("current_character_name", "N/A")
            current_character_id = turn_info.get("current_character_id", None)
            turn_number = turn_info.get("turn_number", 1)
            
            embed = create_embed(
                "Combate Iniciado!",
                f"O combate começou! Turno {turn_number}.",
                discord.Color.green()
            )
            if current_character_id:
                embed.add_field(name="Turno Atual", value=f"**{current_character_name}** (Turno {turn_number})", inline=False)
            else:
                embed.add_field(name="Turno Atual", value=f"Turno {turn_number}", inline=False)
            
            await context.send(embed=embed)

        except CombatSessionNotFoundError as e:
            await context.send(embed=create_embed("Erro de Combate", str(e), discord.Color.red()))
        except CombatError as e:
            await context.send(embed=create_embed("Erro de Combate", f"Erro ao iniciar os turnos: {e}", discord.Color.red()))
        except Exception as e:
            await context.send(embed=create_embed("Erro Inesperado", f"Ocorreu um erro inesperado ao iniciar os turnos: {e}", discord.Color.red()))

    @commands.command(name="proximo")
    async def next_turn(self, context: commands.Context):
        """
        (Mestre) Avança para o próximo turno.
        """
        try:
            session_id = await self.get_session_id_from_context(context)
            
            # Assuming CombatService.next_turn returns info about the next turn
            turn_info = await self.combat_service.next_turn(session_id)
            
            current_character_name = turn_info.get("current_character_name", "N/A")
            current_character_id = turn_info.get("current_character_id", None)
            turn_number = turn_info.get("turn_number", 1)
            
            embed = create_embed(
                "Próximo Turno",
                f"Avançando para o turno {turn_number}.",
                discord.Color.blue()
            )
            if current_character_id:
                embed.add_field(name="Turno Atual", value=f"**{current_character_name}** (Turno {turn_number})", inline=False)
            else:
                embed.add_field(name="Turno Atual", value=f"Turno {turn_number}", inline=False)
            
            await context.send(embed=embed)

        except CombatSessionNotFoundError as e:
            await context.send(embed=create_embed("Erro de Combate", str(e), discord.Color.red()))
        except CombatError as e:
            await context.send(embed=create_embed("Erro de Combate", f"Erro ao avançar para o próximo turno: {e}", discord.Color.red()))
        except Exception as e:
            await context.send(embed=create_embed("Erro Inesperado", f"Ocorreu um erro inesperado ao avançar para o próximo turno: {e}", discord.Color.red()))

    @commands.command(name="dano")
    async def apply_damage(self, context: commands.Context, *args):
        """
        Causa dano a um personagem ou NPC na iniciativa.
        A ordem dos argumentos é flexível.
        Ex: !dano 20 "Orc"
        Ex: !dano "Orc" 20
        Ex: !dano 10
        """
        try:
            quantity, target_name = self._parse_value_and_target(args)
            if quantity is None:
                await context.send(embed=create_embed("Argumento Inválido", "Você precisa fornecer uma quantidade de dano.", discord.Color.red()))
                return

            session_id = await self.get_session_id_from_context(context)
            player_id = str(context.author.id)
            guild_id = str(context.guild.id) if context.guild else "DM"

            target_character_id = None
            actual_target_name = target_name

            if target_name is None:
                # Apply to the player's own character in the current session
                try:
                    session_id, target_character_id = await self.get_player_character_session(context)
                    character = await self.get_character_data(target_character_id, context)
                    if character:
                        actual_target_name = character.name
                    else:
                        raise CharacterNotFoundError("Não foi possível encontrar o seu personagem na sessão.")
                except (CombatSessionNotFoundError, CharacterNotFoundError, InvalidCharacterError):
                    await context.send(embed=create_embed("Erro de Combate", "Você não está em uma sessão de combate ativa ou seu personagem não foi encontrado.", discord.Color.red()))
                    return
            else:
                # Target is specified
                try:
                    character = await self.get_character_data(target_name, context)
                    if character:
                        target_character_id = character.id
                        actual_target_name = character.name
                except (CharacterNotFoundError, InvalidCharacterError):
                    actual_target_name = target_name
                    target_character_id = None

            # Assuming damage is always to HP for now. This might need to be a parameter.
            attribute_type = "hp" 
            
            updated_session = await self.combat_service.apply_damage(
                session_id=session_id,
                target_character_id=str(target_character_id) if target_character_id else None,
                target_name=actual_target_name or "",
                damage_amount=quantity,
                attribute_type=attribute_type,
                player_id=player_id
            )
            
            # Get updated attribute value from the returned CombatSession object
            current_value = "N/A"
            target_entry = next((entry for entry in updated_session.turn_order if (target_character_id and entry.get("id") == target_character_id) or (not target_character_id and entry.get("name") == actual_target_name)), None)
            if target_entry:
                current_value = target_entry.get(attribute_type, "N/A")

            embed = create_embed(
                "Dano Aplicado",
                f"**{quantity}** de dano aplicado a **{actual_target_name}** ({attribute_type.upper()}).",
                discord.Color.orange()
            )
            embed.add_field(name="Novo Valor", value=f"{attribute_type.upper()}: {current_value}", inline=False)
            await context.send(embed=embed)

        except (CombatSessionNotFoundError, InvalidInputError, CombatError, InvalidCharacterError) as e:
            await context.send(embed=create_embed("Erro de Combate", str(e), discord.Color.red()))
        except Exception as e:
            await context.send(embed=create_embed("Erro Inesperado", f"Ocorreu um erro inesperado ao aplicar dano: {e}", discord.Color.red()))

    def _parse_value_and_target(self, args: tuple) -> Tuple[Optional[int], Optional[str]]:
        """Analisa os args para encontrar um valor inteiro e um nome de alvo."""
        value = None
        target = None
        
        str_parts = []
        for arg in args:
            try:
                value = int(arg)
            except ValueError:
                str_parts.append(arg)
        
        if str_parts:
            target = " ".join(str_parts).strip('"')
            
        return value, target

    @commands.command(name="cura")
    async def apply_healing(self, context: commands.Context, *args):
        """
        Cura um personagem ou NPC na iniciativa.
        A ordem dos argumentos é flexível.
        Ex: !cura 15 "Guerreiro"
        Ex: !cura "Guerreiro" 15
        Ex: !cura 10
        """
        try:
            quantity, target_name = self._parse_value_and_target(args)
            if quantity is None:
                await context.send(embed=create_embed("Argumento Inválido", "Você precisa fornecer uma quantidade de cura.", discord.Color.red()))
                return

            session_id = await self.get_session_id_from_context(context)
            player_id = str(context.author.id)
            guild_id = str(context.guild.id) if context.guild else "DM"

            target_character_id = None
            actual_target_name = target_name

            if target_name is None:
                # Apply to the player's own character in the current session
                try:
                    session_id, target_character_id = await self.get_player_character_session(context)
                    character = await self.get_character_data(target_character_id, context)
                    if character:
                        actual_target_name = character.name
                    else:
                        raise CharacterNotFoundError("Não foi possível encontrar o seu personagem na sessão.")
                except (CombatSessionNotFoundError, CharacterNotFoundError, InvalidCharacterError):
                    await context.send(embed=create_embed("Erro de Combate", "Você não está em uma sessão de combate ativa ou seu personagem não foi encontrado.", discord.Color.red()))
                    return
            else:
                # Target is specified
                try:
                    character = await self.get_character_data(target_name, context)
                    if character:
                        target_character_id = character.id
                        actual_target_name = character.name
                except (CharacterNotFoundError, InvalidCharacterError):
                    actual_target_name = target_name
                    target_character_id = None

            # Assuming healing is always to HP for now.
            attribute_type = "hp"
            
            updated_session = await self.combat_service.apply_healing(
                session_id=session_id,
                target_character_id=str(target_character_id) if target_character_id else None,
                target_name=actual_target_name or "",
                heal_amount=quantity,
                attribute_type=attribute_type,
                player_id=player_id
            )
            
            current_value = "N/A"
            target_entry = next((entry for entry in updated_session.turn_order if (target_character_id and entry.get("id") == target_character_id) or (not target_character_id and entry.get("name") == actual_target_name)), None)
            if target_entry:
                current_value = target_entry.get(attribute_type, "N/A")

            embed = create_embed(
                "Cura Aplicada",
                f"**{quantity}** de cura aplicada a **{actual_target_name}** ({attribute_type.upper()}).",
                discord.Color.green()
            )
            embed.add_field(name="Novo Valor", value=f"{attribute_type.upper()}: {current_value}", inline=False)
            await context.send(embed=embed)

        except (CombatSessionNotFoundError, InvalidInputError, CombatError, InvalidCharacterError) as e:
            await context.send(embed=create_embed("Erro de Combate", str(e), discord.Color.red()))
        except Exception as e:
            await context.send(embed=create_embed("Erro Inesperado", f"Ocorreu um erro inesperado ao aplicar cura: {e}", discord.Color.red()))

    @commands.command(name="endcombat")
    async def end_combat(self, context: commands.Context):
        """
        (Mestre) Finaliza a sessão de combate atual.
        """
        try:
            session_id = await self.get_session_id_from_context(context)
            player_id = str(context.author.id)
            
            # Assuming endcombat by default does not persist changes.
            # If persistence is needed, a separate command or flag might be required.
            persist_changes = False 

            # Check if the user is the one who started the combat or a Mestre (simplified check)
            # A more robust check would involve roles or specific Mestre permissions.
            # For now, we'll assume the command is restricted or the CombatService handles it.
            # If the session was started by a different player, we might want to prevent ending it.
            # This requires CombatService to expose who started the session.
            
            # Let's assume CombatService.end_combat_session handles permission checks internally
            # or that the command is only usable by authorized users.
            
            ended = await self.combat_service.end_combat_session(session_id, persist_changes=persist_changes)
            
            if ended:
                embed = create_embed(
                    "Combate Finalizado",
                    f"A sessão de combate `{session_id}` foi finalizada.",
                    discord.Color.blue()
                )
                if persist_changes:
                    embed.description = (embed.description or "") + " As mudanças foram persistidas."
                else:
                    embed.description = (embed.description or "") + " As mudanças foram descartadas."
                await context.send(embed=embed)
            else:
                await context.send(embed=create_embed("Erro de Combate", f"Não foi possível finalizar a sessão de combate `{session_id}`.", discord.Color.red()))

        except (CombatSessionNotFoundError, CharacterNotFoundError, CombatError) as e:
            await context.send(embed=create_embed("Erro de Combate", str(e), discord.Color.red()))
        except Exception as e:
            await context.send(embed=create_embed("Erro Inesperado", f"Ocorreu um erro inesperado ao finalizar o combate: {e}", discord.Color.red()))

async def setup(bot: commands.Bot):
    # Ensure environment variables are set or provide defaults
    mongo_connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    mongo_database_name = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_db = int(os.getenv("REDIS_DB", 0))

    # Instantiate repositories
    mongo_repo = MongoDBRepository(
        connection_string=mongo_connection_string,
        database_name=mongo_database_name,
    )
    await mongo_repo.connect() # Conectar assincronamente
    redis_repo = RedisRepository(
        host=redis_host,
        port=redis_port,
        db=redis_db
    )
    await redis_repo.connect() # Conectar assincronamente
    
    player_preferences_repository = PlayerPreferencesRepository(mongodb_repository=mongo_repo)

    # Instantiate CombatService with repositories
    combat_service = CombatService(character_repository=mongo_repo, session_repository=redis_repo, player_preferences_repository=player_preferences_repository)
    await bot.add_cog(CombatCommands(bot, combat_service))