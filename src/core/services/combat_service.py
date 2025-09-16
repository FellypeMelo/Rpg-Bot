from typing import Optional, Dict, List
from src.core.entities.character import Character
from src.core.entities.combat_session import CombatSession
from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.cache.redis_repository import RedisRepository
from src.utils.exceptions.application_exceptions import CombatError, CombatSessionNotFoundError, CharacterNotFoundError, MaxCombatSessionsError, InvalidInputError
from datetime import datetime, timedelta, timezone

class CombatService:
    def __init__(self, character_repository: MongoDBRepository, session_repository: RedisRepository):
        self.character_repository = character_repository
        self.session_repository = session_repository
        self.MAX_SESSIONS_PER_USER = 3 # Business Rule RN-05

    def start_combat_session(self, character_id: str, guild_id: str, channel_id: str, player_id: str) -> CombatSession:
        character = self.character_repository.get_character(character_id)
        if not character:
            raise CharacterNotFoundError(f"Personagem com ID '{character_id}' não encontrado.")

        # Check for existing sessions for this player
        existing_sessions = self.get_active_combat_sessions_by_player(player_id)
        if len(existing_sessions) >= self.MAX_SESSIONS_PER_USER:
            raise MaxCombatSessionsError(f"Você já tem {self.MAX_SESSIONS_PER_USER} sessões de combate ativas. Finalize uma para iniciar outra.")

        # Create a temporary copy of character attributes for the session
        temporary_attributes = character.to_dict()
        
        # Combat sessions expire after 4 hours of inactivity (RN-05)
        ttl_seconds = int(timedelta(hours=4).total_seconds())

        combat_session = CombatSession(
            character_id=character.id,
            guild_id=guild_id,
            channel_id=channel_id,
            player_id=player_id,
            temporary_attributes=temporary_attributes,
            expires_at=(datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat()
        )
        self.session_repository.save_combat_session(combat_session, ttl_seconds)
        return combat_session

    def get_combat_session(self, session_id: str) -> CombatSession:
        session = self.session_repository.get_combat_session(session_id)
        if not session or not session.is_active:
            raise CombatSessionNotFoundError(f"Sessão de combate com ID '{session_id}' não encontrada ou inativa.")
        session.update_activity()
        self.session_repository.update_combat_session(session)
        return session

    def get_active_combat_sessions_by_player(self, player_id: str) -> List[CombatSession]:
        all_sessions = self.session_repository.get_all_combat_sessions()
        active_sessions = [
            session for session in all_sessions
            if session.player_id == player_id and session.is_active and datetime.fromisoformat(session.expires_at) > datetime.now(timezone.utc)
        ]
        return active_sessions

    def apply_damage(self, session_id: str, attribute_type: str, value: int) -> CombatSession:
        session = self.get_combat_session(session_id) # This also updates activity
        
        if attribute_type not in ["hp", "chakra", "fp"]:
            raise InvalidInputError(f"Tipo de atributo '{attribute_type}' inválido para dano. Use 'hp', 'chakra' ou 'fp'.")
        if value <= 0:
            raise InvalidInputError("Valor de dano deve ser positivo.")

        current_value = session.temporary_attributes.get(attribute_type, 0)
        new_value = max(0, current_value - value)
        session.temporary_attributes[attribute_type] = new_value
        
        self.session_repository.update_combat_session(session)

        if attribute_type == "hp" and new_value == 0:
            # RN-03: HP zero: character incapacitated
            print(f"Alerta: HP do personagem na sessão {session.id} atingiu zero. Personagem incapacitado!")
        elif (attribute_type == "chakra" or attribute_type == "fp") and new_value == 0:
            # RN-03: Chakra/FP zero: cannot use abilities
            print(f"Alerta: {attribute_type.upper()} do personagem na sessão {session.id} atingiu zero. Não pode usar habilidades!")

        return session

    def apply_healing(self, session_id: str, attribute_type: str, value: int) -> CombatSession:
        session = self.get_combat_session(session_id) # This also updates activity

        if attribute_type not in ["hp", "chakra", "fp"]:
            raise InvalidInputError(f"Tipo de atributo '{attribute_type}' inválido para cura. Use 'hp', 'chakra' ou 'fp'.")
        if value <= 0:
            raise InvalidInputError("Valor de cura deve ser positivo.")

        current_value = session.temporary_attributes.get(attribute_type, 0)
        max_value = session.temporary_attributes.get(f"max_{attribute_type}", current_value) # Get max_hp, max_chakra, max_fp
        
        new_value = min(max_value, current_value + value)
        session.temporary_attributes[attribute_type] = new_value

        self.session_repository.update_combat_session(session)
        return session

    def end_combat_session(self, session_id: str, persist_changes: bool = False) -> bool:
        session = self.get_combat_session(session_id) # This also updates activity

        if persist_changes:
            character = self.character_repository.get_character(session.character_id)
            if not character:
                raise CharacterNotFoundError(f"Personagem original com ID '{session.character_id}' não encontrado para persistir mudanças.")
            
            # Apply temporary changes to the permanent character
            for attr_type in ["hp", "chakra", "fp"]:
                character.apply_damage(attr_type, session.temporary_attributes.get(f"max_{attr_type}", 0) - session.temporary_attributes.get(attr_type, 0))
                character.apply_healing(attr_type, session.temporary_attributes.get(attr_type, 0) - character.to_dict().get(attr_type, 0))
            
            self.character_repository.update_character(character)
        
        session.is_active = False
        self.session_repository.delete_combat_session(session.id) # Remove from Redis
        return True