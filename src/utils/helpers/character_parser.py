import re
from typing import Dict, Any

def parse_character_sheet(sheet_text: str) -> Dict[str, Any]:
    """
    Parses a character sheet from a text block into a dictionary.
    """
    data: Dict[str, Any] = {
        "attributes": {},
        "pontos": {"disponiveis": 0}
    }

    # Regex patterns for different sections
    patterns = {
        "name": r"Nome:\s*(.+)",
        "player": r"Jogador:\s*(.+)",
        "level": r"Nível:\s*(\d+)",
        "attributes": r"(For|Dex|Con|Int|Sab|Car):\s*(\d+)",
        "hp": r"Vida:\s*(\d+)\s*/\s*(\d+)",
        "chakra": r"Chakra:\s*(\d+)\s*/\s*(\d+)",
        "fortitude": r"Fortitude:\s*(\d+)\s*/\s*(\d+)",
        "class": r"Classe:\s*(.+)"
    }

    for key, pattern in patterns.items():
        matches = re.findall(pattern, sheet_text)
        if not matches:
            continue

        if key == "attributes":
            for attr, value in matches:
                data["attributes"][attr.lower()] = int(value)
        elif key in ["hp", "chakra", "fortitude"]:
            current, max_val = matches[0]
            resource = key
            if key == "hp":
                resource = "vida"
            data[f"{resource}_atual"] = int(current)
            data[f"{resource}_max"] = int(max_val)
        elif key == "class":
            class_info = matches[0].split('(')
            class_name = class_info[0].strip()
            level_match = re.search(r'\(Lvl:\s*(\d+)\)', matches[0])
            if level_match:
                class_level = int(level_match.group(1))
                data["classes"] = [{"name": class_name, "level": class_level}]
        elif len(matches) == 1:
            data[key] = matches[0] if key not in ["level"] else int(matches[0])

    return data