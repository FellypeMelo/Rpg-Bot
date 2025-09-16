from discord.ext import commands
from typing import Optional
from src.core.services.combat_service import CombatService
from src.application.dtos.combat_dto import StartCombatSessionDTO, ApplyDamageHealingDTO, EndCombatSessionDTO, CombatSessionResponseDTO
from src.utils.exceptions.application_exceptions import CombatError, CombatSessionNotFoundError, CharacterNotFoundError, MaxCombatSessionsError, InvalidInputError
from src.infrastructure.database.mongodb_repository import MongoDBRepository # For instantiation
from src.infrastructure.cache.redis_repository import RedisRepository # For instantiation
import os

class CombatCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, combat_service: CombatService):
        self.bot = bot
        self.combat_service = combat_service

    @commands.command(name="startcombat")
    async def start_combat(self, context: commands.Context, character_id: str):
        """
        Inicia uma sessão de combate para um personagem.
        Ex: !startcombat <ID_DO_PERSONAGEM>
        """
        try:
            start_dto = StartCombatSessionDTO(
                character_id=character_id,
                guild_id=str(context.guild.id) if context.guild else "DM",
                channel_id=str(context.channel.id),
                player_id=str(context.author.id)
            )
            session = self.combat_service.start_combat_session(
                start_dto.character_id,
                start_dto.guild_id,
                start_dto.channel_id,
                start_dto.player_id
            )
            response_dto = CombatSessionResponseDTO(
                id=session.id,
                character_id=session.character_id,
                guild_id=session.guild_id,
                channel_id=session.channel_id,
                player_id=session.player_id,
                start_time=session.start_time,
                last_activity=session.last_activity,
                expires_at=session.expires_at,
                temporary_attributes=session.temporary_attributes,
                is_active=session.is_active
            )
            await context.send(f"Sessão de combate iniciada para o personagem `{response_dto.character_id}`. ID da sessão: `{response_dto.id}`. Expira em: {response_dto.expires_at}")
        except (CharacterNotFoundError, MaxCombatSessionsError, CombatError) as e:
            await context.send(f"Erro ao iniciar combate: {e}")
        except Exception as e:
            await context.send(f"Ocorreu um erro inesperado: {e}")

    @commands.command(name="dano")
    async def apply_damage_command(self, context: commands.Context, session_id: str, attribute_type: str, value: int):
        """
        Aplica dano a um atributo na sessão de combate.
        Tipos: hp, chakra, fp.
        Ex: !dano <ID_DA_SESSAO> hp 20
        """
        try:
            apply_dto = ApplyDamageHealingDTO(session_id=session_id, attribute_type=attribute_type, value=value)
            updated_session = self.combat_service.apply_damage(
                apply_dto.session_id, apply_dto.attribute_type, apply_dto.value
            )
            await context.send(f"Dano de {value} aplicado a {attribute_type.upper()} na sessão `{session_id}`. Novo {attribute_type.upper()}: {updated_session.temporary_attributes.get(attribute_type)}")
        except (CombatSessionNotFoundError, InvalidInputError, CombatError) as e:
            await context.send(f"Erro ao aplicar dano: {e}")
        except Exception as e:
            await context.send(f"Ocorreu um erro inesperado: {e}")

    @commands.command(name="cura")
    async def apply_healing_command(self, context: commands.Context, session_id: str, attribute_type: str, value: int):
        """
        Aplica cura a um atributo na sessão de combate.
        Tipos: hp, chakra, fp.
        Ex: !cura <ID_DA_SESSAO> hp 15
        """
        try:
            apply_dto = ApplyDamageHealingDTO(session_id=session_id, attribute_type=attribute_type, value=value)
            updated_session = self.combat_service.apply_healing(
                apply_dto.session_id, apply_dto.attribute_type, apply_dto.value
            )
            await context.send(f"Cura de {value} aplicada a {attribute_type.upper()} na sessão `{session_id}`. Novo {attribute_type.upper()}: {updated_session.temporary_attributes.get(attribute_type)}")
        except (CombatSessionNotFoundError, InvalidInputError, CombatError) as e:
            await context.send(f"Erro ao aplicar cura: {e}")
        except Exception as e:
            await context.send(f"Ocorreu um erro inesperado: {e}")

    @commands.command(name="endcombat")
    async def end_combat_session_command(self, context: commands.Context, session_id: str, persist: Optional[str] = None):
        """
        Finaliza uma sessão de combate.
        Use --persist para aplicar as mudanças ao personagem permanente.
        Ex: !endcombat <ID_DA_SESSAO>
        Ex: !endcombat <ID_DA_SESSAO> --persist
        """
        try:
            persist_changes = persist == "--persist"
            end_dto = EndCombatSessionDTO(session_id=session_id, persist_changes=persist_changes)
            
            if self.combat_service.end_combat_session(end_dto.session_id, end_dto.persist_changes):
                if persist_changes:
                    await context.send(f"Sessão de combate `{session_id}` finalizada e mudanças persistidas no personagem.")
                else:
                    await context.send(f"Sessão de combate `{session_id}` finalizada e mudanças descartadas.")
            else:
                await context.send(f"Não foi possível finalizar a sessão de combate `{session_id}`.")
        except (CombatSessionNotFoundError, CharacterNotFoundError, CombatError) as e:
            await context.send(f"Erro ao finalizar combate: {e}")
        except Exception as e:
            await context.send(f"Ocorreu um erro inesperado: {e}")

async def setup(bot: commands.Bot):
    mongo_repo = MongoDBRepository(
        connection_string=os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/"),
        database_name=os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db"),
        collection_name=os.getenv("MONGODB_CHARACTER_COLLECTION", "characters")
    )
    redis_repo = RedisRepository(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0))
    )
    combat_service = CombatService(character_repository=mongo_repo, session_repository=redis_repo)
    await bot.add_cog(CombatCommands(bot, combat_service))