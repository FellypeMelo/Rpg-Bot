import re
from typing import Tuple, Optional

class DiceParser:
    @staticmethod
    def parse_dice_notation(dice_notation: str) -> Tuple[int, int, int]:
        """
        Analisa uma notação de dado (ex: '1d6', '2d8+2', '3d4-1') e retorna
        o número de dados, o número de lados e o modificador.
        Retorna (num_dice, num_sides, modifier).
        """
        match = re.match(r'(\d*)d(\d+)([+-]\d+)?', dice_notation.lower())
        if not match:
            raise ValueError(f"Notação de dado inválida: {dice_notation}")

        num_dice = int(match.group(1)) if match.group(1) else 1
        num_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        return num_dice, num_sides, modifier

    @staticmethod
    def format_roll_result(rolls: list[int], total: int, modifier: int = 0) -> str:
        """
        Formata o resultado de uma rolagem de dados para exibição.
        """
        if not rolls:
            return f"Total: {total}"
        
        rolls_str = ", ".join(map(str, rolls))
        if modifier != 0:
            return f"Rolagens: [{rolls_str}] | Modificador: {modifier} | Total: {total}"
        return f"Rolagens: [{rolls_str}] | Total: {total}"