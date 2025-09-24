# src/core/calculators/attribute_roller.py

from src.core.calculators.dice_roller import DiceRoller

def roll_attribute(base_attribute_value: int, modifier: int = 0, additional_bonus: int = 0) -> tuple[int, int]:
    """
    Rola um atributo, adicionando um modificador e um bônus adicional.

    Args:
        base_attribute_value (int): O valor base do atributo (não usado diretamente na
                                    rolagem, mas pode ser usado para contexto futuro).
        modifier (int): O modificador do atributo a ser adicionado à rolagem do dado.
        additional_bonus (int): Um bônus adicional a ser somado ao resultado.

    Returns:
        int: O resultado total da rolagem do atributo.
    """
    d20_roll, _ = DiceRoller.roll_dice("1d20")
    total_roll = d20_roll + modifier + additional_bonus
    return d20_roll, total_roll