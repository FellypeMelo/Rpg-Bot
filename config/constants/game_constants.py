# Game Constants
DEFAULT_ATTRIBUTES = {
    "strength": 10,
    "dexterity": 10,
    "constitution": 10,
    "intelligence": 10,
    "wisdom": 10,
    "charisma": 10
}

# Level Up Bonuses (per level)
LEVEL_UP_BONUSES = {
    "status_points": 3,
    "mastery_points": 2,
    "ph_points": 1
}

# Default Class Templates (can be loaded from JSON or database)
# This is a placeholder for initial setup
DEFAULT_CLASS_TEMPLATES = {
    "Warrior": {
        "name": "Warrior",
        "description": "A strong fighter.",
        "base_attributes": {"strength": 12, "dexterity": 10, "constitution": 14, "intelligence": 8, "wisdom": 10, "charisma": 6},
        "hp_formula": "15d5",
        "chakra_formula": "5d3",
        "fp_formula": "3d4",
        "starting_masteries": {"swords": 2, "shields": 1},
        "starting_skills": ["Cleave", "Shield Bash"],
        "starting_spells": [],
        "level_up_bonuses": LEVEL_UP_BONUSES
    },
    "Guerreiro": {
        "name": "Guerreiro",
        "description": "Um forte lutador.",
        "base_attributes": {"strength": 12, "dexterity": 10, "constitution": 14, "intelligence": 8, "wisdom": 10, "charisma": 6},
        "hp_formula": "15d5",
        "chakra_formula": "5d3",
        "fp_formula": "3d4",
        "starting_masteries": {"swords": 2, "shields": 1},
        "starting_skills": ["Cleave", "Shield Bash"],
        "starting_spells": [],
        "level_up_bonuses": LEVEL_UP_BONUSES
    },
    "Mage": {
        "name": "Mage",
        "description": "A powerful spellcaster.",
        "base_attributes": {"strength": 8, "dexterity": 10, "constitution": 10, "intelligence": 14, "wisdom": 12, "charisma": 6},
        "hp_formula": "8d3",
        "chakra_formula": "12d5",
        "fp_formula": "5d3",
        "starting_masteries": {"arcane": 2},
        "starting_skills": ["Magic Missile", "Arcane Shield"],
        "starting_spells": ["Fireball", "Heal"],
        "level_up_bonuses": LEVEL_UP_BONUSES
    },
    "Mago": {
        "name": "Mago",
        "description": "Um poderoso lançador de feitiços.",
        "base_attributes": {"strength": 8, "dexterity": 10, "constitution": 10, "intelligence": 14, "wisdom": 12, "charisma": 6},
        "hp_formula": "8d3",
        "chakra_formula": "12d5",
        "fp_formula": "5d3",
        "starting_masteries": {"arcane": 2},
        "starting_skills": ["Magic Missile", "Arcane Shield"],
        "starting_spells": ["Fireball", "Heal"],
        "level_up_bonuses": LEVEL_UP_BONUSES
    },
    "Cavaleiro": {
        "name": "Cavaleiro",
        "description": "Formação concedida pelo “Sistema” e também chamada de “definidor de habilidades”, uma Classe é uma configuração que identifica as características mais relevantes de um indivíduo e as organiza para que atendam de forma otimizada às suas necessidades em combate ou em suas funções. Entre inúmeras possibilidades, a Classe “Cavaleiro” foi a que melhor se ajustou a Renée de Lamescour, uma configuração que une elegância, força física e recursos mágicos em perfeito equilíbrio.",
        "base_attributes": {"strength": 15, "dexterity": 15, "constitution": 15, "intelligence": 15, "wisdom": 15, "charisma": 15},
        "hp_formula": "15d5",
        "chakra_formula": "15d5",
        "fp_formula": "15d5",
        "starting_masteries": {},
        "starting_skills": [],
        "starting_spells": [],
        "level_up_bonuses": LEVEL_UP_BONUSES
    }
}