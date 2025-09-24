import re
import secrets

class DiceRoller:
    @staticmethod
    def roll_dice(dice_notation: str) -> tuple[int, int]:
        """
        Rola dados com base na notação de dados (ex: '1d6', '2d8+2', '3d4-1', '1d30!').
        Implementa dados explosivos ('!') onde, se o resultado de um dado for o valor máximo,
        ele é rolado novamente e o resultado é somado. Isso continua enquanto o dado "explodir".
        Retorna o resultado total da rolagem e a contagem de explosões.
        """
        match = re.match(r'(\d*)d(\d+)([+-]\d+)?(!)?', dice_notation.lower())
        if not match:
            raise ValueError(f"Notação de dado inválida: {dice_notation}")

        num_dice = int(match.group(1)) if match.group(1) else 1
        num_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        is_explosive = bool(match.group(4))

        if num_dice <= 0 or num_sides <= 0:
            raise ValueError("Número de dados e lados devem ser maiores que zero.")

        total_roll = 0
        explosion_count = 0

        for _ in range(num_dice):
            current_roll = secrets.randbelow(num_sides) + 1
            total_roll += current_roll

            if is_explosive:
                while current_roll == num_sides:
                    explosion_count += 1
                    current_roll = secrets.randbelow(num_sides) + 1
                    total_roll += current_roll
        
        return total_roll + modifier, explosion_count