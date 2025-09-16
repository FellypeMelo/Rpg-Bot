import math
from typing import Dict

class ModifierCalculator:
    @staticmethod
    def calculate_modifier(status_value: int) -> int:
        """
        Calcula o modificador de um atributo com base na fórmula: floor((Status / 3) - 1).
        """
        return math.floor((status_value / 3) - 1)

    @staticmethod
    def calculate_all_modifiers(attributes: Dict[str, int]) -> Dict[str, int]:
        """
        Calcula os modificadores para todos os atributos fornecidos.
        """
        modifiers = {}
        for attr, value in attributes.items():
            modifiers[attr] = ModifierCalculator.calculate_modifier(value)
        return modifiers