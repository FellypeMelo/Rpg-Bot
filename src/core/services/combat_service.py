import logging
from typing import Any, Optional, List, Dict, Tuple
from src.core.entities.character import Character
from src.core.entities.combat_session import CombatSession
from src.core.calculators.dice_roller import DiceRoller
from src.application.dtos.combat_dto import InitiativeEntryDTO
from src.utils.exceptions.application_exceptions import (
    CombatError,
    CombatSessionNotFoundError,
    CharacterNotFoundError,
    AppPermissionError,
)

class CombatService:
    def __init__(self, character_repository: Any, session_repository: Any, player_preferences_repository: Any):
        self.character_repository = character_repository
        self.session_repository = session_repository
        self.player_preferences_repository = player_preferences_repository
        self.logger = logging.getLogger(__name__)

    async def start_combat_session(self, guild_id: str, channel_id: str, player_id: str) -> CombatSession:
        """Cria e salva uma nova sessão de combate no Redis."""
        self.logger.debug(f"Iniciando start_combat_session para guild_id: {guild_id}, channel_id: {channel_id}, player_id: {player_id}")
        try:
            session = CombatSession(
                guild_id=guild_id,
                channel_id=channel_id,
                player_id=player_id,
                character_id=None,
            )
            self.logger.debug(f"Sessão de combate criada em memória: {session.id}")
            self.logger.debug(f"Chamando session_repository.save_combat_session para session_id: {session.id}")
            await self.session_repository.save_combat_session(session, ttl_seconds=3600)
            self.logger.info(f"Sessão de combate salva no Redis: {session.id}")
            return session
        except Exception as e:
            self.logger.critical(f"Erro inesperado em start_combat_session: {e}", exc_info=True)
            raise CombatError(f"Erro ao iniciar sessão de combate: {e}")

    async def end_combat_session(self, session_id: str, persist_changes: bool = False) -> bool:
        """Encontra e remove a sessão de combate do Redis, opcionalmente persistindo as mudanças."""
        session = await self.session_repository.get_combat_session(session_id)
        if not session:
            raise CombatSessionNotFoundError(f"Nenhuma sessão de combate ativa encontrada para o ID '{session_id}'.")

        if persist_changes:
            for entry in session.turn_order:
                if entry['type'] == 'player':
                    character_id = entry['character_id']
                    character = await self.character_repository.get_character(character_id)
                    if character:
                        character.hp = entry['hp']
                        character.chakra = entry['chakra']
                        character.fp = entry['fp']
                        await self.character_repository.update_character(character)
        
        await self.session_repository.delete_combat_session(session.id)
        return True

    async def add_characters_to_initiative(self, session_id: str, entries: List[InitiativeEntryDTO]) -> CombatSession:
        """Adiciona múltiplos jogadores ou NPCs à ordem de iniciativa."""
        self.logger.debug(f"Iniciando add_characters_to_initiative para session_id: {session_id} com {len(entries)} entradas.")
        try:
            self.logger.debug(f"Chamando session_repository.get_combat_session para session_id: {session_id}")
            session = await self.session_repository.get_combat_session(session_id)
            if not session:
                self.logger.warning(f"CombatSessionNotFoundError em add_characters_to_initiative: Nenhuma sessão de combate ativa encontrada para o ID '{session_id}'.")
                raise CombatSessionNotFoundError(f"Nenhuma sessão de combate ativa encontrada para o ID '{session_id}'.")

            for entry in entries:
                self.logger.debug(f"Processando entrada: {entry.character_name} (NPC: {entry.is_npc})")
                if not entry.is_npc:
                    self.logger.debug(f"Chamando character_repository.get_character para character_id: {entry.character_id}")
                    character = await self.character_repository.get_character(entry.character_id)
                    if not character:
                        self.logger.warning(f"CharacterNotFoundError em add_characters_to_initiative: Personagem com ID '{entry.character_id}' não encontrado.")
                        raise CharacterNotFoundError(f"Personagem com ID '{entry.character_id}' não encontrado.")
                    
                    initiative_roll = DiceRoller.roll_dice("1d20")[0] + entry.modifier
                    self.logger.debug(f"Iniciativa rolada para {character.name}: {initiative_roll} (Modificador: {entry.modifier})")
                    
                    session.add_player_entry(
                        character_id=str(character.id),
                        player_id=character.player_discord_id,
                        name=character.name,
                        initiative=initiative_roll,
                        hp=character.hp,
                        chakra=character.chakra,
                        fp=character.fp
                    )
                    self.logger.info(f"Personagem jogador '{character.name}' adicionado à iniciativa da sessão {session_id}.")
                else:
                    initiative_roll = DiceRoller.roll_dice("1d20")[0] + entry.modifier
                    self.logger.debug(f"Iniciativa rolada para NPC {entry.character_name}: {initiative_roll} (Modificador: {entry.modifier})")
                    session.add_npc_entry(name=entry.character_name, initiative=initiative_roll)
                    self.logger.info(f"NPC '{entry.character_name}' adicionado à iniciativa da sessão {session_id}.")

            self.logger.debug(f"Chamando session_repository.update_combat_session para session_id: {session.id}")
            await self.session_repository.update_combat_session(session)
            self.logger.info(f"Sessão de combate {session.id} atualizada com novos personagens na iniciativa.")
            return session
        except CombatSessionNotFoundError:
            raise
        except CharacterNotFoundError:
            raise
        except Exception as e:
            self.logger.critical(f"Erro inesperado em add_characters_to_initiative: {e}", exc_info=True)
            raise CombatError(f"Erro ao adicionar personagens à iniciativa: {e}")

    async def start_combat_turn(self, session_id: str) -> Dict[str, Any]:
        """Inicia a ordem de turnos, definindo o índice do turno atual como 0."""
        session = await self.session_repository.get_combat_session(session_id)
        if not session:
            raise CombatSessionNotFoundError(f"Nenhuma sessão de combate ativa encontrada para o ID '{session_id}'.")
        
        session.start_battle()
        await self.session_repository.update_combat_session(session)
        
        current_entry = session.get_current_turn_entry()
        return {
            "current_character_name": current_entry['name'],
            "current_character_id": current_entry.get('character_id'),
            "turn_number": session.turn_number
        }

    async def next_turn(self, session_id: str) -> Dict[str, Any]:
        """Avança para o próximo turno na ordem de iniciativa."""
        session = await self.session_repository.get_combat_session(session_id)
        if not session:
            raise CombatSessionNotFoundError(f"Nenhuma sessão de combate ativa encontrada para o ID '{session_id}'.")
        
        session.advance_turn()
        await self.session_repository.update_combat_session(session)
        
        current_entry = session.get_current_turn_entry()
        return {
            "current_character_name": current_entry['name'],
            "current_character_id": current_entry.get('character_id'),
            "turn_number": session.turn_number
        }

    def _verify_ownership(self, player_id: str, target_character_id: Optional[str], target_name: str, session: CombatSession):
        """Verifica se o jogador é o dono do personagem que está tentando usar."""
        target_entry = next((p for p in session.turn_order if p['name'] == target_name and p['type'] == 'player'), None)
        if target_entry and target_entry.get('character_id') == target_character_id and target_entry.get('player_id') != player_id:
            raise AppPermissionError("Você não pode realizar ações por um personagem que não é seu.")
        elif target_entry and target_entry.get('character_id') != target_character_id and target_entry.get('player_id') != player_id:
            # Se o target_character_id não corresponde, mas o player_id sim, pode ser um erro de ID ou nome.
            # Para simplificar, vamos considerar que se o player_id não corresponde, é um erro de permissão.
            # Se o target_character_id é None, significa que o alvo é um NPC ou o nome foi usado para identificar.
            pass # A verificação de NPC ou alvo por nome será feita em apply_damage_to_target

    async def apply_damage(self, session_id: str, target_character_id: Optional[str], target_name: Optional[str], damage_amount: int, attribute_type: str, player_id: str) -> CombatSession:
        """Aplica dano a um alvo na ordem de iniciativa."""
        session = await self.session_repository.get_combat_session(session_id)
        if not session:
            raise CombatSessionNotFoundError(f"Nenhuma sessão de combate ativa encontrada para o ID '{session_id}'.")

        # A verificação de propriedade deve ser mais robusta, considerando NPCs e personagens favoritos.
        # Por enquanto, vamos focar em passar os parâmetros corretos para a sessão.
        # self._verify_ownership(player_id, target_character_id, target_name, session)
        
        try:
            # Passa target_id e target_name para o método da sessão
            session.apply_damage_to_target(amount=damage_amount, target_id=target_character_id, target_name=target_name)
        except KeyError as e:
            raise CombatError(f"Erro ao aplicar dano: {e}")
        except ValueError as e:
            raise CombatError(f"Erro de validação ao aplicar dano: {e}")

        await self.session_repository.update_combat_session(session)
        return session

    async def get_initiative_order(self, session_id: str) -> List[Dict[str, Any]]:
        """Retorna a ordem de iniciativa da sessão de combate."""
        session = await self.session_repository.get_combat_session(session_id)
        if not session:
            raise CombatSessionNotFoundError(f"Nenhuma sessão de combate ativa encontrada para o ID '{session_id}'.")
        return session.turn_order

    async def get_character_by_id(self, character_id: str) -> Optional[Character]:
        """Retorna um personagem pelo seu ID."""
        return await self.character_repository.get_character(character_id)

    async def get_character_by_name(self, name: str) -> Optional[Character]:
        """Retorna um personagem pelo seu nome ou apelido."""
        return await self.character_repository.get_character_by_name_or_alias(name)

    async def get_player_character_session(self, player_id: str, guild_id: str, channel_id: str) -> Tuple[str, str]:
        """
        Encontra a sessão ativa do jogador no canal/guilda e retorna o session_id e o character_id
        do personagem do jogador nessa sessão. Se o jogador tiver um personagem favorito, pode ser usado como fallback.
        """
        self.logger.debug(f"Iniciando get_player_character_session para player_id: {player_id}, guild_id: {guild_id}, channel_id: {channel_id}")
        try:
            self.logger.debug(f"Chamando session_repository.get_combat_session_by_channel para channel_id: {channel_id}")
            session = await self.session_repository.get_combat_session_by_channel(channel_id)
            if session:
                self.logger.debug(f"Sessão encontrada para o canal {channel_id}. Verificando turn_order para player_id: {player_id}")
                for entry in session.turn_order:
                    # Verifica se o player_id corresponde ao owner_id do personagem na turn_order
                    if entry.get('player_id') == player_id:
                        self.logger.info(f"Personagem do jogador '{player_id}' encontrado na sessão '{session.id}'. Character_id: {entry['id']}")
                        return str(session.id), entry['id']
                
                # Se chegou aqui, o jogador não está na turn_order, mas há uma sessão ativa.
                # Vamos usar o personagem favorito como fallback.
                self.logger.debug(f"Jogador {player_id} não encontrado na turn_order da sessão {session.id}. Verificando personagem favorito.")
                player_prefs = await self.player_preferences_repository.get_preferences(player_id)
                if player_prefs and player_prefs.favorite_character_id:
                    self.logger.info(f"Usando personagem favorito {player_prefs.favorite_character_id} como fallback para a sessão {session.id}.")
                    return str(session.id), player_prefs.favorite_character_id

            self.logger.warning(f"CombatSessionNotFoundError em get_player_character_session: Nenhuma sessão de combate ativa encontrada para o jogador '{player_id}' no canal '{channel_id}'.")
            raise CombatSessionNotFoundError(f"Nenhuma sessão de combate ativa encontrada para o jogador '{player_id}' no canal '{channel_id}'.")
        except CombatSessionNotFoundError:
            raise
        except Exception as e:
            self.logger.critical(f"Erro inesperado em get_player_character_session: {e}", exc_info=True)
            raise CombatError(f"Erro ao obter sessão do personagem do jogador: {e}")

    async def get_active_session_id(self, guild_id: str, channel_id: str) -> Optional[str]:
        """Retorna o ID da sessão de combate ativa para o canal, se existir."""
        self.logger.debug(f"Iniciando get_active_session_id para guild_id: {guild_id}, channel_id: {channel_id}")
        try:
            self.logger.debug(f"Chamando session_repository.get_combat_session_by_channel para channel_id: {channel_id}")
            session = await self.session_repository.get_combat_session_by_channel(channel_id)
            if session:
                self.logger.info(f"Sessão ativa encontrada para channel_id: {channel_id}. Session_id: {session.id}")
                return str(session.id)
            self.logger.info(f"Nenhuma sessão ativa encontrada para channel_id: {channel_id}.")
            return None
        except Exception as e:
            self.logger.critical(f"Erro inesperado em get_active_session_id: {e}", exc_info=True)
            raise CombatError(f"Erro ao obter ID da sessão ativa: {e}")

    async def apply_healing(self, session_id: str, target_character_id: Optional[str], target_name: Optional[str], heal_amount: int, attribute_type: str, player_id: str) -> CombatSession:
        """Aplica cura a um alvo na ordem de iniciativa."""
        session = await self.session_repository.get_combat_session(session_id)
        if not session:
            raise CombatSessionNotFoundError(f"Nenhuma sessão de combate ativa encontrada para o ID '{session_id}'.")

        # self._verify_ownership(player_id, target_character_id, target_name, session)

        try:
            session.apply_healing_to_target(amount=heal_amount, target_id=target_character_id, target_name=target_name)
        except KeyError as e:
            raise CombatError(f"Erro ao aplicar cura: {e}")
        except ValueError as e:
            raise CombatError(f"Erro de validação ao aplicar cura: {e}")

        await self.session_repository.update_combat_session(session)
        return session