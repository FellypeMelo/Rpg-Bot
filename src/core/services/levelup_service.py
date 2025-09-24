import asyncio
from src.core.entities.character import Character
from src.core.services.character_service import CharacterService
from src.infrastructure.database.class_repository import ClassRepository
from src.core.calculators.levelup_calculator import calculate_bonuses_for_level
from src.core.calculators.dice_roller import DiceRoller
from src.utils.exceptions.application_exceptions import LevelUpError, CharacterNotFoundError

class LevelUpService:
    def __init__(self, character_service: CharacterService, class_repository: ClassRepository):
        self.character_service = character_service
        self.class_repository = class_repository
        self.character_repository = character_service.character_repository

    async def level_up_character(self, character: Character, levels_to_gain: int) -> Character:
        """
        Aplica o level up direto a um personagem, calculando bônus dinâmicos
        e rolando recursos para todas as suas classes (suporte a multiclasse).
        Não busca o personagem novamente, opera no objeto recebido.
        """
        if not character:
            raise CharacterNotFoundError("Objeto de personagem inválido fornecido para level up.")

        total_hp_gained = 0
        total_chakra_gained = 0
        total_fp_gained = 0
        total_status_points_gained = 0
        total_mastery_points_gained = 0
        total_ph_points_gained = 0

        # Busca todas as classes do personagem para a rolagem multiclasse
        class_tasks = [self.class_repository.get_class(str(cid)) for cid in character.classe_ids]
        character_classes = await asyncio.gather(*class_tasks)

        if not all(character_classes):
            raise LevelUpError("Uma ou mais classes do personagem não foram encontradas no banco de dados.")

        # Calcula bônus e rola recursos para cada nível ganho
        for i in range(levels_to_gain):
            new_level = character.level + 1 + i
            bonuses = calculate_bonuses_for_level(new_level)
            
            total_status_points_gained += bonuses.get("status", 0)
            total_mastery_points_gained += bonuses.get("maestria", 0)
            total_ph_points_gained += bonuses.get("ph", 0)

            # Rola recursos para cada classe e soma os resultados
            for char_class in character_classes:
                if not char_class: continue
                
                hp_roll, _ = DiceRoller.roll_dice(char_class.hp_formula)
                chakra_roll, _ = DiceRoller.roll_dice(char_class.chakra_formula)
                fp_roll, _ = DiceRoller.roll_dice(char_class.fp_formula)
                
                total_hp_gained += hp_roll
                total_chakra_gained += chakra_roll
                total_fp_gained += fp_roll

        # Atualiza os atributos e recursos do personagem
        character.level += levels_to_gain

        character.max_hp += total_hp_gained
        character.hp += total_hp_gained
        character.max_chakra += total_chakra_gained
        character.chakra += total_chakra_gained
        character.max_fp += total_fp_gained
        character.fp += total_fp_gained

        # Adiciona os pontos ganhos aos totais disponíveis
        character.pontos["status"]["total"] += total_status_points_gained
        character.pontos["mastery"]["total"] += total_mastery_points_gained
        character.pontos["ph"]["total"] += total_ph_points_gained
        
        # Recalcula modificadores, caso algum bônus futuro altere atributos base
        character.calculate_modifiers()
        
        await self.character_repository.update_character(character)
        return character

