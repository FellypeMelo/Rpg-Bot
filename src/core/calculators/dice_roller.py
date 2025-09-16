import random
import re

class DiceRoller:
    @staticmethod
    def roll_dice(dice_notation: str) -> int:
        """
        Rola dados com base na notação de dados (ex: '1d6', '2d8+2', '3d4-1').
        Retorna o resultado total da rolagem.
        """
        match = re.match(r'(\d*)d(\d+)([+-]\d+)?', dice_notation.lower())
        if not match:
            raise ValueError(f"Notação de dado inválida: {dice_notation}")

        num_dice = int(match.group(1)) if match.group(1) else 1
        num_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        if num_dice <= 0 or num_sides <= 0:
            raise ValueError("Número de dados e lados devem ser maiores que zero.")

        total_roll = sum(random.randint(1, num_sides) for _ in range(num_dice))
        return total_roll + modifier