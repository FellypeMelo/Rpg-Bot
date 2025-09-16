from typing import Dict, cast
from src.core.calculators.dice_roller import DiceRoller
from src.core.entities.class_template import ClassTemplate # Import ClassTemplate

class AttributeCalculator:
    @staticmethod
    def roll_class_attributes(class_template: ClassTemplate) -> tuple[int, int, int]:
        """
        Rola HP, Chakra e FP com base nas fórmulas definidas no template da classe.
        """
        hp_formula = class_template.hp_formula
        chakra_formula = class_template.chakra_formula
        fp_formula = class_template.fp_formula

        hp = DiceRoller.roll_dice(hp_formula)
        chakra = DiceRoller.roll_dice(chakra_formula)
        fp = DiceRoller.roll_dice(fp_formula)

        return hp, chakra, fp