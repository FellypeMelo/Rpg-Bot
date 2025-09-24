# src/application/commands/points_commands.py

import discord
from discord.ext import commands
from typing import Optional # Import Optional for type hinting
from src.core.services.character_service import CharacterService
# Corrected exception import based on CharacterService.py and application_exceptions.py
from src.utils.exceptions.application_exceptions import CharacterNotFoundError, InvalidInputError
# InsufficientPointsException is not defined in application_exceptions.py, using InvalidInputError for insufficient points.

import os
import discord
from discord.ext import commands
from typing import Optional, Any # Import Any for type hinting
from datetime import datetime, timezone

from src.core.services.character_service import CharacterService
from src.utils.exceptions.application_exceptions import CharacterNotFoundError, InvalidInputError

from src.infrastructure.database.mongodb_repository import MongoDBRepository
from src.infrastructure.database.transformation_repository import TransformationRepository
from src.infrastructure.database.class_repository import ClassRepository

class PointsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, character_service: CharacterService):
        self.bot = bot
        self.character_service = character_service

    async def is_character_owner(self, ctx: commands.Context, character_name: str) -> bool:
        """
        Verifica se o usuário que executou o comando é o dono do personagem.
        """
        try:
            character = await self.character_service.get_character(character_name)
            if character and character.player_discord_id == str(ctx.author.id):
                return True
            else:
                await ctx.send(f"Você não tem permissão para gerenciar o personagem '{character_name}'.")
                return False
        except CharacterNotFoundError:
            await ctx.send(f"Personagem '{character_name}' não encontrado.")
            return False
        except Exception as e:
            print(f"Erro ao verificar propriedade do personagem: {e}")
            await ctx.send("Ocorreu um erro ao verificar a propriedade do personagem.")
            return False

    @commands.group(name='pontos')
    async def points_group(self, ctx: commands.Context):
        """Comandos para gerenciar pontos de status, maestria e PH."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `!pontos pontos <nome_personagem>` para ver seus pontos, ou `!pontos gastar` / `!pontos refund`.")

    @points_group.command(name='pontos')
    async def show_points(self, ctx: commands.Context, character_name: str):
        """Exibe os pontos disponíveis e gastos para um personagem."""
        if not await self.is_character_owner(ctx, character_name):
            return

        try:
            character = await self.character_service.get_character(character_name)

            status_points_data = character.pontos.get("status", {"total": 0, "gasto": 0})
            mastery_points_data = character.pontos.get("mastery", {"total": 0, "gasto": 0})
            ph_points_data = character.pontos.get("ph", {"total": 0, "gasto": []})

            status_available = status_points_data.get("total", 0)
            status_spent = status_points_data.get("gasto", 0)
            mastery_available = mastery_points_data.get("total", 0)
            mastery_spent = mastery_points_data.get("gasto", 0)
            ph_available = ph_points_data.get("total", 0)
            ph_spent_list = ph_points_data.get("gasto", [])

            message = (
                f"**Pontos de '{character_name}':**\n"
                f"- **Status:** Disponíveis: {status_available}, Gastos: {status_spent}\n"
                f"- **Maestria:** Disponíveis: {mastery_available}, Gastos: {mastery_spent}\n"
                f"- **PH:** Disponíveis: {ph_available}, Gastos: {len(ph_spent_list)} entradas"
            )
            if ph_spent_list:
                message += "\n  - Detalhes de PH Gasto:"
                for ph_entry in ph_spent_list:
                    message += f"\n    - '{ph_entry.get('description', 'Sem descrição')}' ({ph_entry.get('points', 0)} pontos)"

            await ctx.send(message)

        except CharacterNotFoundError:
            await ctx.send(f"Personagem '{character_name}' não encontrado.")
        except InvalidInputError as e:
            await ctx.send(f"Erro de entrada: {e}")
        except Exception as e:
            print(f"Erro ao exibir pontos do personagem: {e}")
            await ctx.send("Ocorreu um erro ao buscar os pontos do personagem.")

    @points_group.command(name='gastar')
    async def spend_points(self, ctx: commands.Context, point_type: str, *args):
        """
        Permite gastar pontos de status, maestria ou PH.
        Exemplos:
        !gastar status "Nome" 5
        !gastar maestria "Nome" "Estilo Fogo" 10
        !gastar ph "Nome" 2 "Resistência a Fogo"
        """
        # Flexible argument parsing depending on point_type
        # Expected invocations:
        #  - status: !gastar status <attribute> <character_name> <amount>
        #  - maestria: !gastar maestria <character_name> <amount> <maestria_name>
        #  - ph: !gastar ph <character_name> <amount> <technique_name>
        try:
            # find first token that looks like an integer amount
            amount_idx = None
            for i, a in enumerate(args):
                try:
                    int(a)
                    amount_idx = i
                    break
                except Exception:
                    continue

            if amount_idx is None:
                raise InvalidInputError("Quantidade não informada. Inclua a quantidade como um número.")

            # parse amount
            try:
                amount = int(args[amount_idx])
            except Exception:
                raise InvalidInputError("Quantidade inválida. Use um número inteiro para a quantidade de pontos.")

            # helper to join tokens and strip optional surrounding quotes
            def join_and_strip(tokens):
                s = ' '.join(tokens).strip()
                if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
                    s = s[1:-1]
                return s

            if point_type.lower() == 'status':
                # attribute must be present among args
                valid_attrs = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}
                attr = None
                attr_idx = None
                for i, a in enumerate(args):
                    if a.strip().lower() in valid_attrs:
                        attr = a.strip().lower()
                        attr_idx = i
                        break
                if attr is None:
                    raise InvalidInputError("Atributo alvo não informado ou inválido. Use um dos: strength,dexterity,constitution,intelligence,wisdom,charisma")

                # character name is all tokens excluding attr token and amount token
                name_tokens = [t for idx, t in enumerate(args) if idx not in (attr_idx, amount_idx)]
                character_name = join_and_strip(name_tokens)
                if not character_name:
                    raise InvalidInputError("Nome do personagem não informado.")

                # ownership and fetch
                if not await self.is_character_owner(ctx, character_name):
                    return
                character = await self.character_service.get_character(character_name)
                character.pontos.setdefault("status", {"total": 0, "gasto": 0})
                status_data = character.pontos["status"]
                if status_data["total"] < amount:
                    raise InvalidInputError(f"Pontos de status insuficientes. Disponíveis: {status_data['total']}, Necessários: {amount}")

                # apply points
                current_val = character.attributes.get(attr, 0)
                character.attributes[attr] = current_val + amount
                status_data["total"] -= amount
                status_data["gasto"] = status_data.get("gasto", 0) + amount
                # Recalculate modifiers on the in-memory object and persist atomically
                character.calculate_modifiers()
                await self.character_service.character_repository.update_character(character)
                await ctx.send(f"Gastos {amount} pontos de status em '{attr}' para '{character_name}'.")

            elif point_type.lower() == 'maestria':
                # character name is tokens before amount; description is after
                character_name = join_and_strip(args[:amount_idx])
                description = join_and_strip(args[amount_idx + 1:])
                if not character_name or not description:
                    raise InvalidInputError("Uso: !gastar maestria <nome_personagem> <quantidade> <nome_maestria>")
                if not await self.is_character_owner(ctx, character_name):
                    return
                character = await self.character_service.get_character(character_name)
                character.pontos.setdefault("mastery", {"total": 0, "gasto": 0})
                mastery_data = character.pontos["mastery"]
                if mastery_data["total"] < amount:
                    raise InvalidInputError(f"Pontos de maestria insuficientes. Disponíveis: {mastery_data['total']}, Necessários: {amount}")
                mastery_data["total"] -= amount
                mastery_data["gasto"] = mastery_data.get("gasto", 0) + amount
                # Record the mastery in the character.masteries mapping for display
                description_key = description
                character.masteries = getattr(character, 'masteries', {}) or {}
                character.masteries[description_key] = character.masteries.get(description_key, 0) + amount
                await self.character_service.character_repository.update_character(character)
                await ctx.send(f"Gastos {amount} pontos de maestria ('{description}') para '{character_name}'.")

            elif point_type.lower() == 'ph':
                character_name = join_and_strip(args[:amount_idx])
                description = join_and_strip(args[amount_idx + 1:])
                if not character_name or not description:
                    raise InvalidInputError("Uso: !gastar ph <nome_personagem> <quantidade> <nome_tecnica>")
                if not await self.is_character_owner(ctx, character_name):
                    return
                character = await self.character_service.get_character(character_name)
                character.pontos.setdefault("ph", {"total": 0, "gasto": []})
                ph_data = character.pontos["ph"]
                if ph_data["total"] < amount:
                    raise InvalidInputError(f"Pontos de PH insuficientes. Disponíveis: {ph_data['total']}, Necessários: {amount}")
                ph_data["total"] -= amount
                found = False
                now = datetime.now(timezone.utc)
                for entry in ph_data["gasto"]:
                    # support both 'descricao' (pt) and 'description' (en) stored historically
                    existing_desc = entry.get("descricao") or entry.get("description")
                    if existing_desc == description:
                        # update both common keys for compatibility
                        entry["custo"] = entry.get("custo", entry.get("points", 0)) + amount
                        entry["points"] = entry.get("points", 0) + amount
                        # set or update timestamp
                        entry["data"] = entry.get("data") or now
                        found = True
                        break
                if not found:
                    ph_data["gasto"].append({"descricao": description, "custo": amount, "data": now})
                await self.character_service.character_repository.update_character(character)
                await ctx.send(f"Gastos {amount} pontos de PH ('{description}') para '{character_name}'.")

            else:
                raise InvalidInputError(f"Tipo de ponto inválido: '{point_type}'. Use 'status', 'maestria' ou 'ph'.")

        except CharacterNotFoundError:
            await ctx.send("Personagem não encontrado.")
        except InvalidInputError as e:
            await ctx.send(f"Erro de entrada: {e}")
        except Exception as e:
            print(f"Erro ao gastar pontos: {e}")
            await ctx.send("Ocorreu um erro ao gastar os pontos.")

    # Convenience direct commands as Cog methods so they register when the cog is added
    @commands.command(name='gastar')
    async def cmd_gastar(self, ctx: commands.Context, point_type: str, *args):
        """Shorthand to call the group subcommand: !gastar ... -> delegates to pontos gastar"""
        await self.spend_points(ctx, point_type, *args)

    @points_group.command(name='refund')
    async def refund_points(self, ctx: commands.Context, point_type: str, character_name: str, amount: int, *, description: Optional[str] = None):
        """
        Permite reembolsar pontos gastos (status, maestria, ph).
        Exemplos:
        !refund status "Nome" 5
        !refund maestria "Nome" "Estilo Fogo" 10
        !refund ph "Nome" 2 "Resistência a Fogo"
        """
        if not await self.is_character_owner(ctx, character_name):
            return

        try:
            character = await self.character_service.get_character(character_name)
            
            character.pontos.setdefault("status", {"total": 0, "gasto": 0})
            character.pontos.setdefault("mastery", {"total": 0, "gasto": 0})
            character.pontos.setdefault("ph", {"total": 0, "gasto": []})

            if point_type.lower() == 'status':
                if description:
                    raise InvalidInputError("O tipo 'status' não aceita descrição para reembolso.")
                
                status_data = character.pontos["status"]
                if status_data["gasto"] < amount:
                     raise InvalidInputError(f"Não é possível reembolsar {amount} pontos de status. Gastos totais: {status_data['gasto']}")
                
                status_data["total"] += amount
                status_data["gasto"] = status_data.get("gasto", 0) - amount

            elif point_type.lower() == 'maestria':
                if not description:
                    raise InvalidInputError("O tipo 'maestria' requer uma descrição (ex: nome da maestria) para reembolso.")
                
                mastery_data = character.pontos["mastery"]
                if mastery_data["gasto"] < amount:
                     raise InvalidInputError(f"Não é possível reembolsar {amount} pontos de maestria ('{description}'). Gastos totais: {mastery_data['gasto']}")

                mastery_data["total"] += amount
                mastery_data["gasto"] = mastery_data.get("gasto", 0) - amount

            elif point_type.lower() == 'ph':
                if not description:
                    raise InvalidInputError("O tipo 'ph' requer uma descrição para reembolso.")
                
                ph_data = character.pontos["ph"]
                ph_entry_to_refund = None
                ph_index_to_remove = -1
                for i, entry in enumerate(ph_data["gasto"]):
                    if entry.get("description") == description and entry.get("points") == amount:
                        ph_entry_to_refund = entry
                        ph_index_to_remove = i
                        break
                
                if ph_entry_to_refund is None:
                    raise InvalidInputError(f"Registro de gasto de PH não encontrado para '{description}' com {amount} pontos.")
                
                ph_data["total"] += amount
                if ph_index_to_remove != -1:
                    del ph_data["gasto"][ph_index_to_remove]

            else:
                raise InvalidInputError(f"Tipo de ponto inválido: '{point_type}'. Use 'status', 'maestria' ou 'ph'.")

            await self.character_service.update_character(str(character.id), 'pontos', character.pontos)
            await ctx.send(f"Reembolsados {amount} pontos de {point_type.lower()} para '{character_name}'.")
        except CharacterNotFoundError:
            await ctx.send("Personagem não encontrado.")
        except InvalidInputError as e:
            await ctx.send(f"Erro de entrada: {e}")
        except Exception as e:
            print(f"Erro ao reembolsar pontos: {e}")
            await ctx.send("Ocorreu um erro ao reembolsar os pontos.")

    @commands.command(name='refund')
    async def cmd_refund(self, ctx: commands.Context, point_type: str, character_name: str, amount: int, *, description: Optional[str] = None):
        """Shorthand to call the group subcommand: !refund ... -> delegates to pontos refund"""
        await self.refund_points(ctx, point_type, character_name, amount, description=description)

async def setup(bot: commands.Bot):
    mongo_connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    mongo_database_name = os.getenv("MONGODB_DATABASE_NAME", "rpg_bot_db")

    mongodb_repo = MongoDBRepository(
        connection_string=mongo_connection_string,
        database_name=mongo_database_name
    )
    await mongodb_repo.connect() # Conectar assincronamente
    transformation_repo = TransformationRepository(mongodb_repo)
    class_repo = ClassRepository(mongodb_repo)

    character_service = CharacterService(
        character_repository=mongodb_repo,
        transformation_repository=transformation_repo,
        class_repository=class_repo
    )

    await bot.add_cog(PointsCommands(bot, character_service))